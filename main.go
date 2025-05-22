package main

import (
	"context"
	"devbotagru/utils"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/joho/godotenv"
	"google.golang.org/genai"
)

type chatMessage struct {
	isBot   bool
	message string
}

var (
	embedColor  = utils.ColorBlue // Default colour for embeds
	dangerColor = utils.ColorRed  // Colour for error embeds

	memoryLength = 20 // How many messages to remember (per server) for the chatbot (including the chatbot's replies)

	purgeMinLimit = 1.0
	commands      = []*discordgo.ApplicationCommand{
		{
			Name:        "help",
			Description: "Lists all available commands", // All commands and options must have a description.
		},
		{
			Name:        "dadjoke",
			Description: "Get a random dadjoke.",
		},
		{
			Name:        "joke",
			Description: "Get a random joke.",
		},
		{
			Name:        "fact",
			Description: "Get a random fun fact.",
		},
		{
			Name:        "devbot",
			Description: "Talk to devbot!",
			Options: []*discordgo.ApplicationCommandOption{
				{
					Type:        discordgo.ApplicationCommandOptionString,
					Name:        "prompt",
					Description: "Prompt",
					Required:    true,
				},
			},
		},
		{
			Name:        "purge",
			Description: "Delete last 'n' messages in the current channel",
			Options: []*discordgo.ApplicationCommandOption{
				{
					Type:        discordgo.ApplicationCommandOptionInteger,
					Name:        "n",
					Description: "How many messages to delete",
					Required:    true,
					MinValue:    &purgeMinLimit,
					MaxValue:    50,
				},
			},
		},
	}
	registeredCommands = []*discordgo.ApplicationCommand{}
	chatbotMemory      = make(map[string][]chatMessage)
)

func gemini(history []chatMessage, geminiKey string, systemPrompt string) string {
	ctx := context.Background()

	client, err := genai.NewClient(ctx, &genai.ClientConfig{
		APIKey:  geminiKey,
		Backend: genai.BackendGeminiAPI,
	})
	if err != nil {
		log.Fatal(err)
	}

	messages := []*genai.Content{}

	messages = append(messages, &genai.Content{
		Role: "user",
		Parts: []*genai.Part{
			{Text: fmt.Sprintf("%s In case you need this info, today is %s UTC.", systemPrompt, time.Now().UTC().String())},
		},
	})

	for _, msg := range history {
		if msg.isBot {
			messages = append(messages, &genai.Content{
				Role: "model",
				Parts: []*genai.Part{
					{Text: msg.message},
				},
			})
		} else {
			messages = append(messages, &genai.Content{
				Role: "user",
				Parts: []*genai.Part{
					{Text: msg.message},
				},
			})
		}
	}

	result, err := client.Models.GenerateContent(
		ctx,
		"gemini-1.5-flash",
		messages,
		nil,
	)
	if err != nil {
		log.Fatal(err)
	}
	return result.Text()
}

func cycleStatus(s *discordgo.Session) {
	statuses := []struct{activityType discordgo.ActivityType; body string}{
		{discordgo.ActivityTypeGame, "DevBoiAgru's Games"},
		{discordgo.ActivityTypeGame, "with fire"},
		{discordgo.ActivityTypeWatching, "the world burn"},
		{discordgo.ActivityTypeListening, "the voices"},
		{discordgo.ActivityTypeStreaming, "disappoint parents speedrun (any%) (wr)"},
	}

	go func() {
		i := 0
		for {
			s.UpdateStatusComplex(discordgo.UpdateStatusData{
				Activities: []*discordgo.Activity{
					{
						Name: statuses[i].body,
						Type: statuses[i].activityType,
					},
				},
			})

			i = (i + 1) % len(statuses)
			time.Sleep(30 * time.Second) // change every 30 seconds
		}
	}()
}


func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Couldn't load .env!")
	}

	// Init
	token := os.Getenv("BOT_TOKEN")
	geminiKey := os.Getenv("GEMINI_KEY")
	systemPrompt := os.Getenv("SYSTEM_PROMPT")

	dg, err := discordgo.New("Bot " + token)
	if err != nil {
		log.Fatal(err)
	}
	dg.Identify.Intents = discordgo.IntentsAllWithoutPrivileged

	// Load jokes and fun facts

	// Regular jokes
	jokesFile, err := os.ReadFile("assets/jokes.json")
	if err != nil {
		log.Fatal("Couldn't load jokes.json")
	}
	var regularJokes []map[string]string

	err = json.Unmarshal(jokesFile, &regularJokes)
	if err != nil {
		log.Fatal("Error while unmarshalling json for jokes.json")
	}

	// Dad jokes
	jokesFile, err = os.ReadFile("assets/dadjokes.json")
	if err != nil {
		log.Fatal("Couldn't load dadjokes.json")
	}
	var dadJokes []map[string]string

	err = json.Unmarshal(jokesFile, &dadJokes)
	if err != nil {
		log.Fatal("Error while unmarshalling json for dadjokes.json")
	}

	// Fun facts
	factsFile, err := os.ReadFile("assets/facts.json")
	if err != nil {
		log.Fatal("Couldn't load dadjokes.json")
	}
	var facts []string

	err = json.Unmarshal(factsFile, &facts)
	if err != nil {
		log.Fatal("Error while unmarshalling json for facts.json")
	}

	// Run on login
	dg.AddHandler(func(s *discordgo.Session, r *discordgo.Ready) {
		log.Printf("Logged in as: %v#%v", s.State.User.Username, s.State.User.Discriminator)
	})

	// Run on message create
	dg.AddHandler(func(s *discordgo.Session, m *discordgo.MessageCreate) {
		if m.Author.ID == s.State.User.ID {
			return
		}
	})

	// Add handlers for all the commands
	dg.AddHandler(func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		if i.Type != discordgo.InteractionApplicationCommand {
			return
		}

		switch i.ApplicationCommandData().Name {
		case "help":
			commandHelp := []*discordgo.MessageEmbedField{}
			for _, cmd := range registeredCommands {
				commandHelp = append(commandHelp, &discordgo.MessageEmbedField{
					Name:  "/" + cmd.Name,
					Value: cmd.Description,
				})
			}

			s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseChannelMessageWithSource,
				Data: &discordgo.InteractionResponseData{
					Embeds: []*discordgo.MessageEmbed{{
						Title:       "Helpdesk!",
						Color:       int(embedColor),
						Description: "Here are all available commands:",
						Fields:      commandHelp,
					},
					},
				},
			})

		case "dadjoke":
			dadJoke := dadJokes[rand.Intn(len(dadJokes))]
			s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseChannelMessageWithSource,
				Data: &discordgo.InteractionResponseData{
					Embeds: []*discordgo.MessageEmbed{{
						Title:       "Here's a dad joke!",
						Color:       int(embedColor),
						Description: fmt.Sprintf("%s || %s ||", dadJoke["setup"], dadJoke["punchline"]),
					},
					},
				},
			})

		case "joke":
			joke := regularJokes[rand.Intn(len(regularJokes))]
			s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseChannelMessageWithSource,
				Data: &discordgo.InteractionResponseData{
					Embeds: []*discordgo.MessageEmbed{{
						Title:       "Here's a joke!",
						Color:       int(embedColor),
						Description: fmt.Sprintf("%s || %s ||", joke["setup"], joke["punchline"]),
					},
					},
				},
			})

		case "fact":
			s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseChannelMessageWithSource,
				Data: &discordgo.InteractionResponseData{
					Embeds: []*discordgo.MessageEmbed{{
						Title:       "Here's a fun fact!",
						Color:       int(embedColor),
						Description: facts[rand.Intn(len(facts))],
					},
					},
				},
			})

		case "devbot":
			prompt := i.ApplicationCommandData().Options[0].StringValue()
			if len(prompt) > 250 {
				s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
					Type: discordgo.InteractionResponseChannelMessageWithSource,
					Data: &discordgo.InteractionResponseData{
						Embeds: []*discordgo.MessageEmbed{{
							Title:       "Prompt too long!",
							Color:       int(dangerColor),
							Description: "Use a prompt shorter than 250 characters",
						},
						},
						Flags: discordgo.MessageFlagsEphemeral,
					},
				})
				return
			}

			// Update chatbot memory
			guildMessages := chatbotMemory[i.GuildID]

			if i.Member == nil { // i.Member is nil only if command is NOT used in a guild
				s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
					Type: discordgo.InteractionResponseChannelMessageWithSource,
					Data: &discordgo.InteractionResponseData{
						Embeds: []*discordgo.MessageEmbed{{
							Title:       "Not in a server!",
							Color:       int(dangerColor),
							Description: "You can only use this command in a server.",
						},
						},
						Flags: discordgo.MessageFlagsEphemeral,
					},
				})
				return
			}

			s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseDeferredChannelMessageWithSource,
			})

			if len(guildMessages) > memoryLength {
				guildMessages = guildMessages[1:]
				if cap(guildMessages) > memoryLength*2 {
					tmp := make([]chatMessage, len(guildMessages))
					copy(tmp, guildMessages)
					guildMessages = tmp
				}
			}

			log.Printf("Prompt: %s", prompt)
			guildMessages = append(guildMessages, chatMessage{isBot: false, message: fmt.Sprintf("%s says: %s", i.Member.DisplayName(), prompt)})
			chatbotMemory[i.GuildID] = guildMessages
			
			aiReply := gemini(guildMessages, geminiKey, systemPrompt)
			log.Printf("AI: %s", aiReply)

			guildMessages = append(guildMessages, chatMessage{isBot: true, message: aiReply})
			chatbotMemory[i.GuildID] = guildMessages

			s.FollowupMessageCreate(i.Interaction, false, &discordgo.WebhookParams{
				Embeds: []*discordgo.MessageEmbed{{
					Title:       prompt,
					Color:       int(embedColor),
					Description: aiReply,
					Fields: []*discordgo.MessageEmbedField{
						{
							Name:  "Reply length:",
							Value: fmt.Sprintf("%d characters.", len(aiReply)),
						},
					},
				}},
			})

		case "purge":
			n := i.ApplicationCommandData().Options[0].IntValue()
			
			if i.Member == nil { // i.Member is nil only if command is NOT used in a guild
				s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
					Type: discordgo.InteractionResponseChannelMessageWithSource,
					Data: &discordgo.InteractionResponseData{
						Embeds: []*discordgo.MessageEmbed{{
							Title:       "Not in a server!",
							Color:       int(dangerColor),
							Description: "You can only use this command in a server.",
						},
						},
						Flags: discordgo.MessageFlagsEphemeral,
					},
				})
				return
			}

			// Check if bot has manage messages perms
			botPermissions, err := s.State.UserChannelPermissions(s.State.User.ID, i.ChannelID)
			if err != nil || botPermissions & discordgo.PermissionManageMessages == 0 {
				s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
					Type: discordgo.InteractionResponseChannelMessageWithSource,
					Data: &discordgo.InteractionResponseData{
						Embeds: []*discordgo.MessageEmbed{{
							Title:       "Couldn't purge messages",
							Color:       int(dangerColor),
							Description: "I don't have the necessary permissions to do that.",
						},
						},
						Flags: discordgo.MessageFlagsEphemeral,
					},
				})
				return
			}

			// Check if user has manage messages perms
			userPermissions, err := s.State.UserChannelPermissions(i.Member.User.ID, i.ChannelID)
			if err != nil || userPermissions & discordgo.PermissionManageMessages == 0 {
				s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
					Type: discordgo.InteractionResponseChannelMessageWithSource,
					Data: &discordgo.InteractionResponseData{
						Embeds: []*discordgo.MessageEmbed{{
							Title:       "Couldn't purge messages",
							Color:       int(dangerColor),
							Description: "You don't have the necessary permissions to do that.",
						},
						},
						Flags: discordgo.MessageFlagsEphemeral,
					},
				})
				return
			}

			msgBatch, err := s.ChannelMessages(i.ChannelID, int(n), "", "", "")
			if err != nil {
				s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
					Type: discordgo.InteractionResponseChannelMessageWithSource,
					Data: &discordgo.InteractionResponseData{
						Embeds: []*discordgo.MessageEmbed{{
							Title:       "Couldn't purge messages",
							Color:       int(dangerColor),
							Description: "An error occured while fetching messages.",
						},
						},
						Flags: discordgo.MessageFlagsEphemeral,
					},
				})
				return
			}

			for _, msg := range msgBatch {
				err := s.ChannelMessageDelete(i.ChannelID, msg.ID)
				if err != nil {
					s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
						Type: discordgo.InteractionResponseChannelMessageWithSource,
						Data: &discordgo.InteractionResponseData{
							Embeds: []*discordgo.MessageEmbed{{
								Title:       "Couldn't purge messages",
								Color:       int(dangerColor),
								Description: "An error occured while deleting messages.",
							},
							},
							Flags: discordgo.MessageFlagsEphemeral,
						},
					})
					return
				}
			}

			s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseChannelMessageWithSource,
				Data: &discordgo.InteractionResponseData{
					Content: fmt.Sprintf("Deleted %d message(s)!", n),
					Flags:   discordgo.MessageFlagsEphemeral,
				},
			},
			)


		}
	})

	// Open the websocket connection
	err = dg.Open()
	if err != nil {
		log.Fatal(err)
	}

	// Start cycling statuses
	cycleStatus(dg)

	// Register commands
	for _, v := range commands {

		if v.Name == "devbot" && geminiKey == "" {
			// Skip if gemini key isn't provided
			log.Printf("Skipping chatbot command since Gemini API key is not provided.")
			continue
		}

		cmd, err := dg.ApplicationCommandCreate(dg.State.User.ID, "", v)
		if err != nil {
			log.Panicf("Cannot create '%v' command: %v", v.Name, err)
		}
		registeredCommands = append(registeredCommands, cmd)
	}
	log.Printf("Registered %d commands.", len(registeredCommands))

	if err != nil {
		log.Fatal(err)
	}
	defer dg.Close()

	sc := make(chan os.Signal, 1)
	signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt)
	<-sc

	log.Println("Removing commands...")

	// Delete commands we registered on exit
	for _, cmd := range registeredCommands {
		err := dg.ApplicationCommandDelete(dg.State.User.ID, "", cmd.ID)
		if err != nil {
			log.Panicf("Cannot delete '%v' command: %v", cmd.Name, err)
		}
	}

	log.Println("Shut down gracefully.")
}

package com.example.examplemod;


import com.example.examplemod.utils.ScoreboardUtils;
import com.example.examplemod.utils.requestsUtil;
import net.minecraft.client.Minecraft;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.util.text.TextComponentString;
import net.minecraftforge.client.event.ClientChatReceivedEvent;
import net.minecraftforge.client.event.RenderGameOverlayEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;

import java.io.FileWriter;
import java.io.IOException;
import java.util.*;
import  org.apache.logging.log4j.Logger;

public class eventsForge {

    // Minecraft logger
    Logger logger;
    // Saving minecraft as variable so that we dont do everytime Minecraft.getMinecraft()
    Minecraft mc;
    // We need inWar for then sending the endWar packet with players
    boolean inWar = false, doneWar = false;
    // Same of inWar
    String lastTer = "";
    // Yes.
    public static final boolean DEBUG = true;

    // Bank Logger class that contains a transaction
    static class logMessages {
        String name, item;
        int quantity;
        long time;
        boolean withdraw;
        public logMessages(String name, String item, int quantity, boolean withdraw) {
            this.name = name;
            this.item = item;
            this.quantity = quantity;
            this.withdraw = withdraw;
            time = new Date().getTime();
        }

        @Override
        public String toString() {
            return time + " " + name + " " + item + " " + quantity + " " + (withdraw ? 1 : 0);
        }
    }

    // This contains every transactions, and we'll use this for then creating the log file
    Queue<logMessages> messages = new LinkedList<>();

    public eventsForge(String path, long startTime, Logger logger) {
        this.logger = logger;
        this.mc = Minecraft.getMinecraft();
        /*Nothing was in this line*/
        // Write the bank logger when minecraft is shutting down
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            try {
                // Write.
                FileWriter fw = new FileWriter(path + "/" + startTime + "-" + new Date().getTime() + ".txt");

                while(!messages.isEmpty()) {
                    fw.write(messages.remove().toString() + "\n");
                }

                fw.close();
            }catch (IOException ignored) {

            }
        }));
    }

    /*
        When we are in a war, check the name of the terr based on the bossbar
     */
    @SubscribeEvent
    public void onOverlay(RenderGameOverlayEvent.Pre event) {
        if (inWar && event.getType() == RenderGameOverlayEvent.ElementType.BOSSINFO) {
            // Get name of the boss
            String name = ((RenderGameOverlayEvent.BossInfo) event).getBossInfo().getName().getUnformattedText();
            // When we are in war the only bass bar that contains [ is the tower bossbarr
            if (name.split(" ")[0].contains("[")) {
                // Here we just extract the name of the terr with some hardcoded stuff
                name = name.substring(name.indexOf("]") + 4);
                name = name.substring(0, name.indexOf("§"));
                name = name.replace(" ", "_");
                // Get every player that is near us
                StringBuilder players = new StringBuilder();
                boolean first = true;
                for(EntityPlayer e : mc.world.playerEntities) {
                    // We are adding , because of the request
                    players.append(first ? "" : ",").append(e.getName());
                    first = false;
                }
                // Request!
                requestsUtil.makeRequest(String.format("startWar?terr=%s&players=%s", name, players), false);
                // This will be used for endWar; only people that were in a ffa are gonna have lastTer not empty
                lastTer = name;
                // We dont want to spam the server
                inWar = false;
            }

        }
    }

    @SubscribeEvent
    public void onMessage(ClientChatReceivedEvent event) {
        String message = event.getMessage().getUnformattedText();
        String[] messages = message.split(" ");
        /* Nothing was in this line */
        // Bank logger
        if (messages.length > 3 && messages[0].contains("INFO")) {
            boolean withdraw = false;
            if (messages[2].equals("withdrew")) {
                withdraw = true;
            // This should not happen, but better then sorry
            } else if (!messages[2].equals("deposited")) {
                return;
            }
            // Hardcoded stuff for extracting data
            String name = messages[1];
            int num = Integer.parseInt(messages[3].split("x")[0]);
            int startIndexing = message.indexOf(messages[3]) + messages[3].length();
            String nameItem = message.substring(startIndexing, (withdraw ? message.indexOf(" from ") : message.indexOf(" to ")));
            // Save
            this.messages.add(new logMessages(name, nameItem, num, withdraw));
        // So we received a message about a war?!
        } else if (messages[0].equals("§3[WAR§3]")) {
            // If a war started
            if (message.contains("The battle has begun!")) {
                // TODO i forgot the check with the scoreboard if we were in a war
                /* Function that check if we are actually in war */
                // We are in war!
                inWar = true;

                // Remember me to remove this
                doneWar = true;
                requestsUtil.makeRequest("test", false);
            // We captured a terr
            } else if(message.contains("You have taken control of") && doneWar) {
                // Get the name of the terr
                String terr = message.substring(message.indexOf("You have taken control of") + "You have taken control of".length());
                terr = terr.split("from")[0];
                terr = terr.substring(1, terr.length() - 1);
                terr = terr.replace(" ", "_");
                boolean notInWar = true;
                // Prepare the request
                String request = "endWar?";
                if (terr.equals(lastTer)) {
                    // TODO make this a function
                    List<String> scores = ScoreboardUtils.getSidebarScores(mc.world.getScoreboard());
                    for(String score : scores) {
                        if (score.contains("§3[WAR]")) {
                            // Then we are in war
                            notInWar = false;
                            break;
                        }
                    }
                    // The bossbar is cooler
                    /*
                    if (!notInWar) {
                        StringBuilder players = new StringBuilder();
                        boolean first = true;
                        for(EntityPlayer e : mc.world.playerEntities) {
                            players.append(first ? "" : ",").append(e.getName());
                            first = false;
                        }
                        request += String.format("players=%s&situation=true&location=%s", players, terr);
                    }*/
                }
                if (notInWar) {
                    request += String.format("situation=true&location=%s", terr);
                }
                requestsUtil.makeRequest(request);
            // L we lost
            } else if(message.contains("has lost the war") && doneWar) {
                String terr = message.substring(message.indexOf("for") + "for".length());
                terr = terr.substring(1, terr.length() - 1);
                terr = terr.replace(" ", "_");
                if (!terr.contains("]"))
                    // Log that we lost so that we can create that funny thing for bullying peter
                    requestsUtil.makeRequest("endWar?situation=false&location=" + terr);

            }
        }
    }

    // Just for testing stuff
    void sendClientMessage(String message) {
        Minecraft.getMinecraft().player.sendMessage(new TextComponentString(message));
    }

}



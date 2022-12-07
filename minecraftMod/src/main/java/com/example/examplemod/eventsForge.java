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

    Logger logger;
    Minecraft mc;
    boolean inWar = false, doneWar = false;
    String lastTer = "";

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

    Queue<logMessages> messages = new LinkedList<>();

    public eventsForge(String path, long startTime, Logger logger) {
        this.logger = logger;
        this.mc = Minecraft.getMinecraft();
        this.logger.info("Token:" + mc.getSession().getToken());
        // Write the file of the bank logger
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            try {
                FileWriter fw = new FileWriter(path + "/" + startTime + "-" + new Date().getTime() + ".txt");

                while(!messages.isEmpty()) {
                    fw.write(messages.remove().toString() + "\n");
                }

                fw.close();
            }catch (IOException ignored) {

            }
        }));
        /*
        §3[INFO§3] Ascended_Winter deposited 1x Fizzy Beverage of Blessings [1/3]À to the Guild Bank (High Ranked)
        §3[INFO§3] Magicmakerman withdrew 1x PirateÀÀÀCove Teleport Scroll from the Guild Bank (Everyone)
        §3[INFO§3] Magicmakerman deposited 30x PirateÀÀÀCove Teleport Scroll to the Guild Bank (Everyone)
         */
    }

    @SubscribeEvent
    public void onOverlay(RenderGameOverlayEvent.Pre event) {
        if (inWar && event.getType() == RenderGameOverlayEvent.ElementType.BOSSINFO) {
            String name = ((RenderGameOverlayEvent.BossInfo) event).getBossInfo().getName().getUnformattedText();
            if (name.split(" ")[0].contains("[")) {
                name = name.substring(name.indexOf("]") + 4);
                name = name.substring(0, name.indexOf("§"));
                name = name.replace(" ", "_");
                StringBuilder players = new StringBuilder();
                boolean first = true;
                for(EntityPlayer e : mc.world.playerEntities) {
                    players.append(first ? "" : ",").append(e.getName());
                    first = false;
                }
                requestsUtil.makeRequest(String.format("startWar?terr=%s&players=%s", name, players), false);
                lastTer = name;
                inWar = false;
            }

        }
    }

    @SubscribeEvent
    public void onMessage(ClientChatReceivedEvent event) {
        String message = event.getMessage().getUnformattedText();
        String[] messages = message.split(" ");
        if (messages[0].equals("§c❤"))
            return;
        // Bank logger
        if (messages.length > 3 && messages[0].contains("INFO")) {
            boolean withdraw = false;
            if (messages[2].equals("withdrew")) {
                withdraw = true;
            } else if (!messages[2].equals("deposited")) {
                return;
            }
            String name = messages[1];
            int num = Integer.parseInt(messages[3].split("x")[0]);
            int startIndexing = message.indexOf(messages[3]) + messages[3].length();
            String nameItem = message.substring(startIndexing, (withdraw ? message.indexOf(" from ") : message.indexOf(" to ")));
            this.messages.add(new logMessages(name, nameItem, num, withdraw));
        } else if (messages[0].equals("§3[WAR§3]")) {
            if (message.contains("The battle has begun!")) {
                inWar = true;
                doneWar = true;
                requestsUtil.makeRequest("test", false);
            } else if(message.contains("You have taken control of") && doneWar) {
                String terr = message.substring(message.indexOf("You have taken control of") + "You have taken control of".length());
                terr = terr.split("from")[0];
                terr = terr.substring(1, terr.length() - 1);
                terr = terr.replace(" ", "_");
                boolean notInWar = true;
                String request = "endWar?";
                if (terr.equals(lastTer)) {
                    List<String> scores = ScoreboardUtils.getSidebarScores(mc.world.getScoreboard());
                    for(String score : scores) {
                        if (score.contains("§3[WAR]")) {
                            notInWar = false;
                            break;
                        }
                    }
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
            } else if(message.contains("has lost the war") && doneWar) {
                String terr = message.substring(message.indexOf("for") + "for".length());
                terr = terr.substring(0, terr.length() - 1);
                terr = terr.replace(" ", "_");
                requestsUtil.makeRequest("endWar?situation=false&location=" + terr);

            }
        }
    }

    // Just for testing stuff
    void sendClientMessage(String message) {
        Minecraft.getMinecraft().player.sendMessage(new TextComponentString(message));
    }

}



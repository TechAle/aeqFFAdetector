package com.example.examplemod.utils;

import net.minecraft.client.Minecraft;
import net.minecraft.util.text.TextComponentString;

import java.net.HttpURLConnection;
import java.net.URL;

public class requestsUtil {

    static String ip = "http://127.0.0.1:5000/";

    public static void makeRequest(String args) {
        makeRequest(args, true);
    }

    /*
        True: Get
        False: Post
     */
    public static void makeRequest(String args, boolean type) {
        try {
            if (Minecraft.getMinecraft().player != null)
                sendClientMessage("Sent packet " + ip + args + " with " + (type ? "GET" : "POST"));

            URL url = new URL(ip + args);

            HttpURLConnection conn = (HttpURLConnection)url.openConnection();
            conn.setRequestMethod(type ? "GET" : "POST");
            for (String[] header : new String[][]{
                    {"Accept", "Text/html"},
                    {"Cache-Control", "no-cache"},
                    {"test", ""},
                    {"Connection", "close"},
                    {"User-Agent", "aeq"}
            }) {
                conn.setRequestProperty(header[0], header[1]);
            }
            conn.getInputStream();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }


    // Just for testing stuff
    static void sendClientMessage(String message) {
        Minecraft.getMinecraft().player.sendMessage(new TextComponentString(message));
    }

}

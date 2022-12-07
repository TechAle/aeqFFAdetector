package com.example.examplemod;

import com.example.examplemod.utils.requestsUtil;
import net.minecraft.client.Minecraft;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.common.Mod.EventHandler;
import net.minecraftforge.fml.common.event.FMLInitializationEvent;
import net.minecraftforge.fml.common.event.FMLPreInitializationEvent;
import org.apache.logging.log4j.Logger;

import java.io.File;
import java.util.Date;

@Mod(modid = ExampleMod.MODID, name = ExampleMod.NAME, version = ExampleMod.VERSION)
public class ExampleMod
{
    public static final String MODID = "examplemod";
    public static final String NAME = "Example Mod";
    public static final String VERSION = "1.0";

    private static Logger logger;
    private String path;
    private long startTime;

    @EventHandler
    public void preInit(FMLPreInitializationEvent event)
    {
        Minecraft mc = Minecraft.getMinecraft();
        logger = event.getModLog();
        File aeq = new File(mc.mcDataDir, "/aeq");
        if (!aeq.exists())
            //noinspection ResultOfMethodCallIgnored
            aeq.mkdirs();

        File bank = new File(mc.mcDataDir + "/aeq/bank");
        if (!bank.exists())
            //noinspection ResultOfMethodCallIgnored
            bank.mkdirs();
        path = new File(mc.mcDataDir + "/aeq/bank").getAbsolutePath();
        // This is used for the name of the bank logger file
        startTime = new Date().getTime();
    }

    @EventHandler
    public void init(FMLInitializationEvent event)
    {
        requestsUtil.makeRequest("discover?player=" + Minecraft.getMinecraft().getSession().getUsername());
        MinecraftForge.EVENT_BUS.register(new eventsForge(path, startTime, logger));


    }


}

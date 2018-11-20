package com.travelsky.redis;

import java.io.File;

public class Config {
    public static final String SEPARATOR = System.getProperty("file.separator");
    public static final String PACKAGE_NAME = getPackageName();
    public static final String LOCALDB_PATH = getLocalDbPath();

    private static String getLocalDbPath() {
        String dirName = "localDB";
        String dbFileName = "redisValueOffsetRecord.db";
        return System.getProperty("user.dir") + SEPARATOR + dirName + SEPARATOR + dbFileName;
    }

    private static String getPackageName(){
        return Config.class.getPackage().getName() + ".";
    }



    public static void main(String[] args) {
        System.out.println(Config.PACKAGE_NAME);
        System.out.println(File.separator);
        System.out.println(LOCALDB_PATH);
        String packageName = Config.class.getPackage().getName();
        System.out.println(Config.class);
        System.out.println(Config.class.getPackage().getName());


    }
}

package com.travelsky.redis;


import org.quartz.*;
import org.quartz.impl.StdSchedulerFactory;

import static org.quartz.JobBuilder.*;
import static org.quartz.TriggerBuilder.*;
import static org.quartz.SimpleScheduleBuilder.*;



public class QuartzTest {

    public static void main(String[] args) throws SchedulerException {




        // Grab the Scheduler instance from the Factory
        Scheduler scheduler = StdSchedulerFactory.getDefaultScheduler();

        // and start it off
        scheduler.start();

        // define the job and tie it to our HelloJob class
        JobDetail job = newJob(Hahaworld.class)
                .withIdentity("job1", "group1")
                .build();

        // Trigger the job to run now, and then repeat every 40 seconds
        Trigger trigger = newTrigger()
                .withIdentity("trigger1", "group1")
//
                .withSchedule(SimpleScheduleBuilder
                        .simpleSchedule()
                        .withIntervalInSeconds(4)
                        .repeatForever())
                .startNow()
                .build();

        // Tell quartz to schedule the job using our trigger
        scheduler.scheduleJob(job, trigger);
        scheduler.shutdown();


    }
}


class Hahaworld implements Job {

    @Override
    public void execute(JobExecutionContext context) throws JobExecutionException {
        System.out.println("sdf");

    }
}
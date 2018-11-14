package com.travelsky.redis;


import com.alibaba.fastjson.JSON;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class JsonDemo {

    public static void main(String[] args){

        Group[] group = {new Group(), new Group()};
        group[0].setId(0L);
        group[0].setName("admin");

        User guestUser0 = new User();
        guestUser0.setId(2L);
        guestUser0.setName("guest");

        User rootUser0 = new User();
        rootUser0.setId(3L);
        rootUser0.setName("root");

        group[0].addUser(guestUser0);
        group[0].addUser(rootUser0);


        group[1].setId(0L);
        group[1].setName("admin1");

        User guestUser1 = new User();
        guestUser1.setId(2L);
        guestUser1.setName("guest1");

        User rootUser1 = new User();
        rootUser1.setId(3L);
        rootUser1.setName("root1");

        group[1].addUser(guestUser1);
        group[1].addUser(rootUser1);


        Map<String, Group> obj = new HashMap<>();
        obj.put("grp0", group[0]);
        obj.put("grp1", group[1]);
        String jsonString = JSON.toJSONString(obj);

        System.out.println(jsonString);
    }
}


class User {

    private Long id;
    private String name;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}

class Group {

    private Long id;
    private String name;
    private List<User> users = new ArrayList<>();

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public List<User> getUsers() {
        return users;
    }

    public void setUsers(List<User> user) {
        this.users = user;
    }

    public void addUser(User user) {
        users.add(user);
    }
}
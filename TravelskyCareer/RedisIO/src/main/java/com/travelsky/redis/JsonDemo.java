package com.travelsky.redis;


import com.alibaba.fastjson.JSON;

import java.util.ArrayList;
import java.util.List;

public class JsonDemo {

    public static void main(String[] args){

        Group group = new Group();
        group.setId(0L);
        group.setName("admin");

        U guestUser = new U();
        guestUser.setId(2L);
        guestUser.setName("guest");

        U rootUser = new U();
        rootUser.setId(3L);
        rootUser.setName("root");

        group.addUser(guestUser);
        group.addUser(rootUser);

        String jsonString = JSON.toJSONString(group);

        System.out.println(jsonString);
    }
}


class U {

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
    private List<U> u = new ArrayList<U>();

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

    public List<U> getUsers() {
        return u;
    }

    public void setUsers(List<U> user) {
        this.u = user;
    }

    public void addUser(U user) {
        u.add(user);
    }
}
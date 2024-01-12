/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Modalities;

import scxmlgen.interfaces.IModality;

/**
 *
 * @author nunof
 */
public enum Touch implements IModality{

    SELECT("[GESTURES][SELECT]",5000), //COMPLEMENTAR
    DELETE_EVENT("[GESTURES][DELETE]",5000), //REDUNDANTE
    
  
    ;
    
    private String event;
    private int timeout;


    Touch(String m, int time) {
        event=m;
        timeout=time;
    }

    @Override
    public int getTimeOut() {
        return timeout;
    }

    @Override
    public String getEventName() {
        //return getModalityName()+"."+event;
        return event;
    }

    @Override
    public String getEvName() {
        return getModalityName().toLowerCase()+event.toLowerCase();
    }
    
}
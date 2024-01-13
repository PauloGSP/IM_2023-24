package Modalities;

import scxmlgen.interfaces.IOutput;

public enum Output implements IOutput{
    
    DELETE_EVENT("[FUSION][DELETE_EVENT]"),
    SELECT("[FUSION][SELECT]"),
    CHANGE_EVENT_DATE("[FUSION][CHANGE_EVENT_DATE]"),
    PROVIDE_DATE("[FUSION][PROVIDE_DATE]"),
    PROVIDE_DAY("[FUSION][PROVIDE_DAY]"),
    ;
    
    
    
    private String event;

    Output(String m) {
        event=m;
    }
    
    public String getEvent(){
        return this.toString();
    }

    public String getEventName(){
        return event;
    }
}

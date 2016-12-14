package com.saral;

import java.text.SimpleDateFormat;
import java.util.Collection;
import java.util.Date;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.propertyeditors.CustomDateEditor;
import org.springframework.web.bind.WebDataBinder;
import org.springframework.web.bind.annotation.InitBinder;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

import com.saral.model.TimeTrackRecord;
import com.saral.services.TimeTrackRecordService;


@RestController
public class TimeTrackController {

	@Autowired
	private TimeTrackRecordService service;
    
	@InitBinder
    public void initBinder(WebDataBinder binder) {
        SimpleDateFormat dateFormat = new SimpleDateFormat("dd.MM.yyyy HH:mm");
        dateFormat.setLenient(false);
        binder.registerCustomEditor(Date.class, new CustomDateEditor(dateFormat, false));
    }
	
    @RequestMapping("/records")
    public Collection<TimeTrackRecord> get(String email) {
    	return email == null ? service.findAll() : service.findByEmployee(email);
    }
    
    @RequestMapping(value = "/records", method = RequestMethod.POST)
    public TimeTrackRecord put(TimeTrackRecord record) {
    	return service.recordTimeTrack(record);
    }    
}

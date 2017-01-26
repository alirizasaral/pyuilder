package com.saral.employee.controller;

import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Collection;
import java.util.Date;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.beans.propertyeditors.CustomDateEditor;
import org.springframework.web.bind.WebDataBinder;
import org.springframework.web.bind.annotation.InitBinder;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.saral.employee.controller.model.TimeTrackRecord;
import com.saral.employee.controller.services.TimeTrackRecordService;


@RestController
public class TimeTrackController {

	@Autowired
	private TimeTrackRecordService service;
	
	@Value("${simulation.delay}")
	private int delay;
    
	@InitBinder
    public void initBinder(WebDataBinder binder) {
        SimpleDateFormat dateFormat = new SimpleDateFormat("dd.MM.yyyy HH:mm");
        dateFormat.setLenient(false);
        binder.registerCustomEditor(Date.class, new CustomDateEditor(dateFormat, false));
    }
	
    @RequestMapping("/records")
    public Collection<TimeTrackRecord> get(String email, 
    									   @RequestParam(value = "offset", defaultValue = "0", required = false) int offset, 
    									   @RequestParam(value = "length", defaultValue = "-1", required = false) int length) throws InterruptedException {
    	Collection<TimeTrackRecord> records = email == null ? service.findAll() : service.findByEmployee(email);
    	Collection<TimeTrackRecord> result = transformResult(records, offset, length);
    	simulateDelay(result.size());
		return result;
    }
    
    private void simulateDelay(int size) throws InterruptedException {
    	Thread.sleep(delay * size);
	}

	private Collection<TimeTrackRecord> transformResult(Collection<TimeTrackRecord> result, int offset, int length) {
    	TimeTrackRecord[] records = result.toArray(new TimeTrackRecord[1]);
    	return Arrays.asList(Arrays.copyOfRange(records, offset, length == -1 ? records.length : offset + length));
	}

	@RequestMapping(value = "/records", method = RequestMethod.POST)
    public TimeTrackRecord put(TimeTrackRecord record) {
    	return service.recordTimeTrack(record);
    }    
}

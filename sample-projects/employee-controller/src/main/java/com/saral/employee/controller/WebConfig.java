/**
 * 
 */
package com.saral.employee.controller;

import java.util.Date;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.event.ContextRefreshedEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

import com.saral.employee.controller.services.TimeTrackRecordGenerator;
import com.saral.employee.controller.services.TimeTrackRecordService;

/**
 * @author Ali Riza Saral <Ali-Riza-Savas.Saral@allianz.at>
 *
 */
@Component
public class WebConfig {
	
	@Autowired
	private TimeTrackRecordGenerator generator;
	
	@Autowired
	private TimeTrackRecordService service;

	@Value("${simulation.email}")
	private String email;

	@Value("${simulation.entries}")
	private int numberOfEntries;
	
	@EventListener({ContextRefreshedEvent.class})
	void configure() {
		generateRecords();
	}

	private void generateRecords() {
		generator.generate(email, new Date(), numberOfEntries, service);
	}
}

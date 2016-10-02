package com.saral;

import java.util.Arrays;
import java.util.Collection;
import java.util.Date;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;


@RestController
public class TimeTrackController {

	public static final class TimeTrackRecord {
		public Date start;
		public Date end; 

		public TimeTrackRecord(Date start, Date end) {
			this.start = start;
			this.end = end;
		}
	}
	
    @RequestMapping("/records")
    public Collection<TimeTrackRecord> get() {
    	return Arrays.asList(new TimeTrackRecord(new Date(), new Date()), new TimeTrackRecord(new Date(), new Date()), new TimeTrackRecord(new Date(), new Date()));
    }
}

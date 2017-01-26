/**
 * 
 */
package com.saral.employee.controller.services;

import java.util.Calendar;
import java.util.Date;

import org.springframework.stereotype.Component;

import com.saral.employee.controller.model.TimeTrackRecord;

/**
 * @author Ali Riza Saral <Ali-Riza-Savas.Saral@allianz.at>
 *
 */
@Component
public class TimeTrackRecordGenerator {

	public void generate(String email, Date from, int numberOfEntries, TimeTrackRecordService service) {
		Calendar calendar = Calendar.getInstance();
		calendar.setTime(from);
		
		for (int i = 0; i < numberOfEntries; i++) {
			TimeTrackRecord record = generate(email, calendar);
			service.recordTimeTrack(record);
			calendar.add(Calendar.HOUR, 2);
		}
	}

	private TimeTrackRecord generate(String email, Calendar calendar) {
		Date start = calendar.getTime();
		calendar.add(Calendar.HOUR, 1);
		Date end = calendar.getTime();
		return new TimeTrackRecord(start, end, email);
	}
}

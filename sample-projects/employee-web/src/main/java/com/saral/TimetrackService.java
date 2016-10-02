package com.saral;

import java.util.Date;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;
import com.mashape.unirest.http.exceptions.UnirestException;

@Service
public class TimetrackService {
	
	@Value("${timetrack.service.url}")
	private String serviceURL;

	public static final class TimeTrackRecord {
		public Date start;
		public Date end;

		public TimeTrackRecord() {
			// NOOP
		}
		
		public TimeTrackRecord(Date start, Date end) {
			this.start = start;
			this.end = end;
		}
	}
	
	public TimeTrackRecord[] getRecords() throws UnirestException {
		HttpResponse<TimeTrackRecord[]> response = Unirest.get(serviceURL).asObject(TimeTrackRecord[].class);
		if (response.getStatus() != 200) {
			throw new RuntimeException("Got invalid response from timetrack-service at " + serviceURL + ": " + response.getStatus() + ", " + response.getStatusText());
		}
		return response.getBody();
	}
}

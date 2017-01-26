/**
 * 
 */
package com.saral.employee.controller.model;

import java.util.Date;

/**
 * @author Ali Riza Saral <Ali-Riza-Savas.Saral@allianz.at>
 *
 */
public class TimeTrackRecord {
	
	private Date start;
	private Date end; 
	private String email;
	
	public TimeTrackRecord(Date start, Date end, String email) {
		this.start = start;
		this.end = end;
		this.email = email;
	}
	
	public TimeTrackRecord() {
		// NOOP
	}
	
	public Date getStart() {
		return start;
	}
	public void setStart(Date start) {
		this.start = start;
	}
	public Date getEnd() {
		return end;
	}
	public void setEnd(Date end) {
		this.end = end;
	}
	public String getEmail() {
		return email;
	}
	public void setEmail(String email) {
		this.email = email;
	}
}

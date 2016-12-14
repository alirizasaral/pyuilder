/**
 * 
 */
package com.saral.services;

import java.util.Collection;
import java.util.Collections;
import java.util.LinkedList;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.stereotype.Component;

import com.saral.model.TimeTrackRecord;

/**
 * @author Ali Riza Saral <Ali-Riza-Savas.Saral@allianz.at>
 *
 */
@Component
public class TimeTrackRecordService {

	private final Map<String, Collection<TimeTrackRecord>> records = new ConcurrentHashMap<>();
	private final Collection<TimeTrackRecord> allRecords = Collections.synchronizedList(new LinkedList<>());
	
	public TimeTrackRecord recordTimeTrack(TimeTrackRecord record) {
		Collection<TimeTrackRecord> bucket = getOrCreateRecordBucket(record.getEmail());
		bucket.add(record);
		allRecords.add(record);
		return record;
	}
	
	private Collection<TimeTrackRecord> getOrCreateRecordBucket(String email) {
		Collection<TimeTrackRecord> bucket = records.get(email);
		if (bucket == null) {
			bucket = Collections.synchronizedList(new LinkedList<>());
			records.put(email, bucket);
		}
		return bucket;
	}

	public Collection<TimeTrackRecord> findByEmployee(String email) {
		Collection<TimeTrackRecord> result = records.get(email);
		return result == null ? Collections.EMPTY_LIST : Collections.unmodifiableCollection(result);
	}

	public Collection<TimeTrackRecord> findAll() {
		return Collections.unmodifiableCollection(allRecords);
	}


}

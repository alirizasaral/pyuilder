package com.saral;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

import com.mashape.unirest.http.exceptions.UnirestException;

@Controller
public class HomeController {

	private final Logger LOGGER = Logger.getLogger(HomeController.class.getName());
	
	@Autowired
	private TimetrackService timeTrackService;
	
    @RequestMapping("/")
    public String greeting(@RequestParam(value="name", required=false, defaultValue="John Doe") String name, Model model) {
        model.addAttribute("name", name);
        try {
			model.addAttribute("records", timeTrackService.getRecords());
		} catch (UnirestException e) {
			LOGGER.log(Level.SEVERE, e.getMessage(), e);
			model.addAttribute("error", "Cannot retrieve time-records: " + e.getMessage());
		}
        return "home";
    }

}
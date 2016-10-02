package com.saral;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class EmployeeWebApplication {

	public static void main(String[] args) {
		new UnirestConfiguration().setObjectMapper();
		SpringApplication.run(EmployeeWebApplication.class, args);
	}
}

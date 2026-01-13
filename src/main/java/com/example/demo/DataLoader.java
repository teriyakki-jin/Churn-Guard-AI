package com.example.demo;

import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

@Component
public class DataLoader {

    @Autowired
    private CustomerRepository customerRepository;

    @PostConstruct
    public void loadData() {
        if (customerRepository.count() > 0) {
            System.out.println("Data already loaded, skipping.");
            return;
        }

        try (BufferedReader br = new BufferedReader(
                new InputStreamReader(new ClassPathResource("Customer-Churn.csv").getInputStream()))) {
            String line;
            boolean isFirstLine = true;
            List<Customer> customers = new ArrayList<>();

            while ((line = br.readLine()) != null) {
                if (isFirstLine) {
                    isFirstLine = false;
                    continue;
                }

                String[] data = line.split(",(?=([^\"]*\"[^\"]*\")*[^\"]*$)", -1); // Handle quotes if any, though
                                                                                   // simplified split might work for
                                                                                   // this dataset

                // Assuming standard CSV format from the notebook:
                // customerID,gender,SeniorCitizen,Partner,Dependents,tenure,PhoneService,MultipleLines,InternetService,OnlineSecurity,OnlineBackup,DeviceProtection,TechSupport,StreamingTV,StreamingMovies,Contract,PaperlessBilling,PaymentMethod,MonthlyCharges,TotalCharges,Churn

                Customer customer = new Customer();
                customer.setCustomerId(data[0]);
                customer.setGender(data[1]);
                customer.setSeniorCitizen(Integer.parseInt(data[2]));
                customer.setPartner(data[3]);
                customer.setDependents(data[4]);
                customer.setTenure(Integer.parseInt(data[5]));
                customer.setPhoneService(data[6]);
                customer.setMultipleLines(data[7]);
                customer.setInternetService(data[8]);
                customer.setOnlineSecurity(data[9]);
                customer.setOnlineBackup(data[10]);
                customer.setDeviceProtection(data[11]);
                customer.setTechSupport(data[12]);
                customer.setStreamingTV(data[13]);
                customer.setStreamingMovies(data[14]);
                customer.setContract(data[15]);
                customer.setPaperlessBilling(data[16]);
                customer.setPaymentMethod(data[17]);
                customer.setMonthlyCharges(Double.parseDouble(data[18]));

                // Handle TotalCharges which might be empty string " "
                String totalChargesStr = data[19].trim();
                if (totalChargesStr.isEmpty() || totalChargesStr.equals(" ")) {
                    customer.setTotalCharges(0.0);
                } else {
                    customer.setTotalCharges(Double.parseDouble(totalChargesStr));
                }

                customer.setChurn(data[20]);

                customers.add(customer);
            }

            customerRepository.saveAll(customers);
            System.out.println("Loaded " + customers.size() + " customers into H2 database.");

        } catch (Exception e) {
            System.err.println("Failed to load CSV data: " + e.getMessage());
            e.printStackTrace();
        }
    }
}

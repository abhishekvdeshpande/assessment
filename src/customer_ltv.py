import json
import csv
import re
from datetime import datetime

from customer import Customer
from site_visit import SiteVisit
from orders import Orders
from images import Images


def get_week_number_since_start(date):
    # Reference date (January 1, 1 AD)
    reference_date = datetime(1, 1, 1)

    # Calculate the difference in weeks
    weeks_difference = (date - reference_date).days // 7

    # Adjust for the starting week
    week_number = weeks_difference + 1

    return week_number


# The procedure involves taking in the events, cleansing them, associating each one with the corresponding customers,
# and then updating the relevant information, ultimately storing it in the respective object.
def ingest(e, D):

    for obj in e:
        # Acceptable object types - CUSTOMER, SITE_VISIT, IMAGE and ORDER
        obj_type = obj.get("type", None)
        obj_verb = obj.get("verb", None)
        key = obj.get("key", None)
        event_time = obj.get("event_time", None)
        # All the if conditions below are used to verify whether the event contains the
        # necessary/mandatory fields for processing the data.
        if obj_type and obj_verb and key and event_time:
            if obj_type == "CUSTOMER":
                last_name = obj.get("last_name", None)
                city = obj.get("adr_city", None)
                state = obj.get("adr_state", None)
                # New Customer
                if key not in D:
                    D[key] = Customer(event_time, last_name, city, state)
                else:
                    # Existing Customer updated
                    D[key].update_customer(event_time, last_name, city, state)

            else:
                cid = obj.get("customer_id", None)
                if cid in D:
                    if obj_type == "SITE_VISIT":
                        tags = obj.get("tags", None)
                        sv_obj = SiteVisit(key, event_time, tags)
                        D[cid].details["site_visits"].append(sv_obj)

                    if obj_type == "IMAGE":
                        make = obj.get("camera_make")
                        model = obj.get("camera_model")
                        img_obj = Images(key, event_time, make, model)
                        D[cid].details["images"].append(img_obj)

                    if obj_type == "ORDER":
                        amount = obj.get("total_amount", None)
                        if amount:
                            # Cleaning the total amount to sum up the same later
                            # We could also develop in future extracting the currency separate and tracking it as required
                            amount = float(re.sub(r"[^0-9.]", "", amount))
                            ord_obj = Orders(key, event_time, amount)

                            # In case of updates the pop_order_by_id method pops the order maintained in a max heap
                            # and updates the required properties and adds it back to the orders with updated event_ts
                            # This helps in tracking the latest order of the user efficiently
                            if obj_verb == "UPDATE":
                                popped_ord = D[cid].pop_order_by_id(key)
                                D[cid].details["total_amount"] -= popped_ord.order_data["amount"]
                            D[cid].add_order(ord_obj)

    return D


# Method to generate Lifetime value of Customers
def get_ltv_list(D):

    result = []
    for key, value in customers.items():
        # Fetch created on date, identify the beginning week of the customer
        date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        created_on_date_string = datetime.strptime(value.details["created_on"], date_format)
        created_week = get_week_number_since_start(created_on_date_string)
        latest_week = created_week
        # Identify the last updated week of the customer available in events received
        if value.details["orders"]:
            latest_order_date = value.details["orders"][0][1].order_data["event_time"]
            latest_order_date_string = datetime.strptime(latest_order_date, date_format)
            latest_week = get_week_number_since_start(latest_order_date_string)
        # To compute the average Lifetime Value (LTV), it is assumed that the customer has been a customer for at least
        # a year, considering either 52 weeks or the available data.
        # For instance, if Customer A's data is present in both week 1 and week 2, and
        # Customer B is present only in week 1, then the LTV of A is greater than that of B.
        # This distinction is made based on the number of weeks present,
        # assuming a yearly calculation for a span of 10 years.
        weeks = max(52, latest_week-created_week+1)
        total_visits = len(value.details["site_visits"])
        # Expenditure per visit required to calculate "a"
        # i.e. sum of all orders amount of the customer divided by total number of site visits
        exp_per_visit = value.details["total_amount"] / total_visits
        # Visits per week required to calculate "a"
        # i.e. Total number of visits by the customer, and number of weeks of a year or greater (as visited)
        visit_per_week = total_visits/weeks
        # LTV of each customer - 52*a*10
        ltv = (exp_per_visit*visit_per_week) * 52 * 10
        temp = (key, ltv)
        result.append(temp)

    return result

# Method to return the top x customers with their highest LTV's
def TopXSimpleLTVCustomers(x, D):
    sorted_list_desc = sorted(D, key=lambda i: i[1], reverse=True)
    # If the customer list is smaller than the x return all the customers
    if len(sorted_list_desc) <= x:
        return sorted_list_desc

    # Below logic to include all the customers to be returned with same LTVs under one rank
    rank = 0
    return_list = []
    for ind, each in enumerate(sorted_list_desc):
        if ind == 0:
            return_list.append(each)
            rank += 1
        else:
            if not return_list[-1][1] == each[1]:
                rank += 1
            return_list.append(each)
        if rank == x + 1:
            break
    return return_list


if __name__ == "__main__":

    file_name = "day_1"
    folder_path = f"../input/{file_name}.txt"

    # Date to hold all customer data ingested
    customers = {}
    json_data = None

    # Reading the input file as JSON data
    with open(f"{folder_path}", 'r') as file:
        json_data = json.load(file)

    # Ingesting the events read
    customers = ingest(json_data, customers)
    # Get LTV for all the customers ingested
    ltv_list = get_ltv_list(customers)
    # Extract the list of top X customers with the highest LTV
    top_customers = TopXSimpleLTVCustomers(10, ltv_list)

    output_filename = f'../output/{file_name}.csv'
    headers = ['customer_ID', 'LTV']

    # Write the data to the CSV file
    with open(output_filename, 'w', newline='') as file:
        writer = csv.writer(file)

        # Write the headers
        writer.writerow(headers)

        # Write the data
        writer.writerows(top_customers)

    print(f'Data has been written to {output_filename}.')

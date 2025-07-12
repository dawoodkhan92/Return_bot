#!/usr/bin/env python3
"""
Test data generator for customer journey scenarios.

This script generates realistic test scenarios for customer returns with randomized
data to test various edge cases and conversation patterns.
"""

import json
import random
import argparse
from datetime import datetime, timedelta
import uuid


def generate_test_data(num_scenarios=10):
    """Generate additional test scenarios for customer journeys"""
    scenarios = []
    
    # Define possible values for randomization
    return_reasons = [
        "wrong_size", "defective", "not_as_described", "changed_mind", 
        "unwanted_gift", "damaged_in_shipping", "incorrect_item", "poor_quality"
    ]
    
    products = [
        {"name": "Classic T-Shirt", "price": 29.99, "category": "clothing"},
        {"name": "Denim Jeans", "price": 59.99, "category": "clothing"},
        {"name": "Summer Dress", "price": 89.99, "category": "clothing"},
        {"name": "Running Shoes", "price": 129.99, "category": "footwear"},
        {"name": "Winter Jacket", "price": 199.99, "category": "outerwear"},
        {"name": "Baseball Cap", "price": 24.99, "category": "accessories"},
        {"name": "Cotton Socks", "price": 12.99, "category": "clothing"},
        {"name": "Wool Sweater", "price": 79.99, "category": "clothing"},
        {"name": "Leather Boots", "price": 159.99, "category": "footwear"},
        {"name": "Silk Scarf", "price": 49.99, "category": "accessories"},
        {"name": "Phone Case", "price": 19.99, "category": "electronics"},
        {"name": "Bluetooth Headphones", "price": 89.99, "category": "electronics"},
        {"name": "Yoga Mat", "price": 39.99, "category": "fitness"},
        {"name": "Water Bottle", "price": 24.99, "category": "fitness"}
    ]
    
    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Edward", "Fiona", 
                   "George", "Helen", "Ian", "Julia", "Kevin", "Linda", "Michael", "Nancy"]
    last_names = ["Smith", "Jones", "Brown", "Wilson", "Taylor", "Davis", "White", "Clark",
                  "Anderson", "Thomas", "Jackson", "Harris", "Martin", "Thompson", "Garcia", "Martinez"]
    
    # Conversation patterns for different scenarios
    conversation_patterns = {
        "basic_return": [
            "I want to return {product}",
            "My order number is {order_id}",
            "The reason is {reason}",
            "Yes, I have the original packaging"
        ],
        "email_lookup": [
            "I need to return something I ordered",
            "I don't have the order number but my email is {email}",
            "It was {product}",
            "The problem is {reason}"
        ],
        "urgent_return": [
            "I need to return {product} immediately",
            "Order {order_id}",
            "This is {reason}",
            "How quickly can this be processed?"
        ],
        "confused_customer": [
            "Hi, I have a problem with my order",
            "I'm not sure how to return something",
            "I bought {product}",
            "Order {order_id}",
            "It's {reason}"
        ],
        "international": [
            "Hello, I want to return an item",
            "I'm in {country}",
            "Order number {order_id}",
            "The {product} is {reason}",
            "Do I need to pay for return shipping?"
        ]
    }
    
    countries = ["Canada", "UK", "Germany", "France", "Australia", "Japan", "Italy", "Spain"]
    
    for i in range(num_scenarios):
        # Generate random customer
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        customer = {
            "id": f"cust_{uuid.uuid4().hex[:8]}",
            "name": f"{first_name} {last_name}",
            "email": f"{first_name.lower()}.{last_name.lower()}@example.com"
        }
        
        # Add country for some customers (international scenarios)
        if random.random() > 0.8:
            customer["country"] = random.choice(countries)
        
        # Generate random order
        num_items = random.randint(1, 4)
        items = []
        total = 0
        
        for j in range(num_items):
            product = random.choice(products)
            quantity = random.randint(1, 2)
            item = {
                "id": f"gid://shopify/LineItem/item_{uuid.uuid4().hex[:8]}",
                "name": product["name"],
                "price": str(product["price"]),
                "quantity": quantity,
                "variant": {
                    "id": f"gid://shopify/ProductVariant/var_{uuid.uuid4().hex[:8]}",
                    "title": f"Standard / {random.choice(['Red', 'Blue', 'Black', 'White', 'Green'])}",
                    "sku": f"{product['category'].upper()}-{random.randint(100, 999)}"
                }
            }
            items.append(item)
            total += product["price"] * quantity
        
        # Randomize order date (1-50 days ago to test various policy scenarios)
        days_ago = random.randint(1, 50)
        order_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        order_id = f"ord_{uuid.uuid4().hex[:8]}"
        order_name = f"#{random.randint(1000, 9999)}"
        
        order = {
            "id": f"gid://shopify/Order/{order_id}",
            "name": order_name,
            "date": order_date,
            "items": items,
            "total": str(round(total, 2)),
            "financial_status": "paid",
            "fulfillment_status": "fulfilled"
        }
        
        # Add shipping info for some orders
        if random.random() > 0.7:
            order["shipping"] = {
                "method": random.choice(["standard", "express", "international"]),
                "cost": str(round(random.uniform(5.99, 35.99), 2)),
                "tracking": f"TRK{random.randint(100000000, 999999999)}"
            }
        
        # Generate conversation flow based on pattern
        return_reason = random.choice(return_reasons)
        main_product = random.choice(items)["name"]
        
        # Choose conversation pattern
        if "country" in customer:
            pattern_type = "international"
        elif random.random() > 0.9:
            pattern_type = "urgent_return"
        elif random.random() > 0.8:
            pattern_type = "email_lookup"
        elif random.random() > 0.7:
            pattern_type = "confused_customer"
        else:
            pattern_type = "basic_return"
        
        conversation_flow = []
        pattern = conversation_patterns[pattern_type]
        
        for message_template in pattern:
            message = message_template.format(
                product=main_product,
                order_id=order_name,
                reason=return_reason.replace("_", " "),
                email=customer["email"],
                country=customer.get("country", "")
            )
            conversation_flow.append(message)
        
        # Add some randomized follow-up messages
        follow_ups = [
            "How long will the refund take to process?",
            "Do I need to pay for return shipping?",
            "Can I get store credit instead?",
            "Is there a return label I can print?",
            "What's your return policy?",
            "Can I exchange this for a different size?",
            "I need this processed urgently",
            "Will I get a full refund?",
            "Can someone call me about this?"
        ]
        
        # Add 0-3 random follow-up questions
        num_followups = random.randint(0, 3)
        for _ in range(num_followups):
            if random.random() > 0.5:
                conversation_flow.append(random.choice(follow_ups))
        
        # Create the complete scenario
        scenario = {
            "name": f"generated_scenario_{i+1}",
            "customer": customer,
            "order": order,
            "return_reason": return_reason,
            "conversation_pattern": pattern_type,
            "conversation_flow": conversation_flow,
            "days_since_order": days_ago,
            "order_value": total,
            "generated_at": datetime.now().isoformat()
        }
        
        scenarios.append(scenario)
    
    return scenarios


def save_scenarios(scenarios, filename="generated_scenarios.json"):
    """Save scenarios to a JSON file"""
    with open(filename, "w") as f:
        json.dump(scenarios, f, indent=2)
    
    print(f"Generated {len(scenarios)} test scenarios and saved to {filename}")
    
    # Print summary statistics
    reasons = [s["return_reason"] for s in scenarios]
    patterns = [s["conversation_pattern"] for s in scenarios]
    
    print(f"\nScenario Summary:")
    print(f"- Return Reasons: {dict((r, reasons.count(r)) for r in set(reasons))}")
    print(f"- Conversation Patterns: {dict((p, patterns.count(p)) for p in set(patterns))}")
    print(f"- International Orders: {sum(1 for s in scenarios if 'country' in s['customer'])}")
    print(f"- High Value Orders (>$200): {sum(1 for s in scenarios if s['order_value'] > 200)}")
    print(f"- Policy Violations (>30 days): {sum(1 for s in scenarios if s['days_since_order'] > 30)}")


def main():
    parser = argparse.ArgumentParser(description="Generate customer journey test scenarios")
    parser.add_argument("--scenarios", type=int, default=20,
                        help="Number of scenarios to generate (default: 20)")
    parser.add_argument("--output", default="tests/e2e/generated_scenarios.json",
                        help="Output file path (default: tests/e2e/generated_scenarios.json)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducible generation")
    
    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}")
    
    # Generate scenarios
    scenarios = generate_test_data(args.scenarios)
    
    # Save to file
    save_scenarios(scenarios, args.output)


if __name__ == "__main__":
    main() 
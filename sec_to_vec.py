"""Push SEC filings to Weaviate."""
import os
import sys
import cohere
import weaviate
from dotenv import load_dotenv

from tools.utils import create_arg_parser

# Get the secrets
load_dotenv()
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
co_api_key = os.getenv("COHERE_API_KEY")

weaviate_client = weaviate.Client(
    url="https://cohere-ycm-hackathon-narbqtfd.weaviate.network",
    auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_api_key),
)
co_client = cohere.Client(co_api_key)


SCHEMA = {
    "classes": [
        {
            "class": "f10k",
            "description": "Storing 10K filings",
            "properties": [
                {
                    "name": "business",
                    "dataType": ["text"],
                    "description": "Item 1. Business",
                },
                {
                    "name": "risk",
                    "dataType": ["text"],
                    "description": "Item 1A. Risk Factors",
                },
                {
                    "name": "staff",
                    "dataType": ["text"],
                    "description": "Item 1B. Unresolved Staff Comments",
                },
                {
                    "name": "properties",
                    "dataType": ["text"],
                    "description": "Item 2. Properties",
                },
                {
                    "name": "legal",
                    "dataType": ["text"],
                    "description": "Item 3. Legal Proceedings",
                },
                {
                    "name": "mine",
                    "dataType": ["text"],
                    "description": "Item 4. Mine Safety Disclosures",
                },
                {
                    "name": "market",
                    "dataType": ["text"],
                    "description": "Item 5. Market for Registrant’s Common Equity, Related Stockholder Matters and Issuer Purchases of Equity Securities",
                },
                {
                    "name": "reserved",
                    "dataType": ["text"],
                    "description": "Item 6. Reserved",
                },
                {
                    "name": "management",
                    "dataType": ["text"],
                    "description": "Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations",
                },
                {
                    "name": "disclosure",
                    "dataType": ["text"],
                    "description": "Item 7A. Quantitative and Qualitative Disclosures About Market Risk",
                },
                {
                    "name": "financials",
                    "dataType": ["text"],
                    "description": "Item 8. Financial Statements and Supplementary Data",
                },
                {
                    "name": "changes",
                    "dataType": ["text"],
                    "description": "Item 9. Changes in and Disagreements With Accountants on Accounting and Financial Disclosure",
                },
                {
                    "name": "controls",
                    "dataType": ["text"],
                    "description": "Item 9A. Controls and Procedures",
                },
                {
                    "name": "other",
                    "dataType": ["text"],
                    "description": "Item 9B. Other Information",
                },
                {
                    "name": "foreign",
                    "dataType": ["text"],
                    "description": "Item 9C. Disclosure Regarding Foreign Jurisdictions that Prevent Inspection",
                },
                {
                    "name": "officers",
                    "dataType": ["text"],
                    "description": "Item 10. Directors, Executive Officers and Corporate Governance",
                },
                {
                    "name": "executive",
                    "dataType": ["text"],
                    "description": "Item 11. Executive Compensation",
                },
                {
                    "name": "security",
                    "dataType": ["text"],
                    "description": "Item 12. Security Ownership of Certain Beneficial Owners and Management and Related Stockholder Matters",
                },
                {
                    "name": "transactions",
                    "dataType": ["text"],
                    "description": "Item 13. Certain Relationships and Related Transactions, and Director Independence",
                },
                {
                    "name": "fees",
                    "dataType": ["text"],
                    "description": "Item 14. Principal Accountant Fees and Services",
                },
                {
                    "name": "exhibits",
                    "dataType": ["text"],
                    "description": "Item 15. Exhibits, Financial Statement Schedules",
                },
            ],
        }
    ]
}


# weaviate_client.schema.create(SCHEMA)

# text = "Your text here"
# response = co_client.embed(model='large', texts=[text])
# embedding = response.embeddings[0]

# data_object = {
#     "text": text,
#     "embedding": embedding
# }

# weaviate_client.data_object.create(data_object, "TextData")


if __name__ == "__main__":
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args(sys.argv[1:])

    if args.schema:
        import yaml

        print("Creating schema.")
        print(yaml.dump(SCHEMA, default_flow_style=False))
        weaviate_client.schema.create(SCHEMA)

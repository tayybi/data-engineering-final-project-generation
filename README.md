# group-2-data-engineering-final-project

# Table of Contents

1. [Project Description](#project-description) 
2. [Client Requirements](#client-requirements)
3. [Installation](#installation)
4. [Ways of Working](#ways-of-working)
5. [Sprint 1](#sprint-1)
	1. [ETL Pipeline](#etl-pipeline)
	2. [Github Actions](#github-actions)
	3. [Data Normalisation](#data-normalisation)
	4. [Database Connection](#database-connection)
	5. [Docker](#docker)
6. [Sprint 2]
    1. [AWS Setup getting things ready]
	1. [Create ETL Lambda]
	2. [Modify ETL Lambda to be called by S3]
    3. [Modify ETL Lambda to load data into redshift]
7. [Sprint 3]
	1. [Setup Grafana Infrastructure]
	2. [Setup Grafana Data Source]
    3. [Setup Grafana Data Source(CloudWatch)]
8. [Sprint 4]
	1. [Contineue...]

## Project Description

This project was undertaken as a group, as part of the data engineering course provided by Generation & UK and Ireland. The problem we were confronted with was that of a pop-up cafe owner who wanted software to aggregate sales data from all of their store branches into a single database. Their current setup involves the following steps that happen concurrently at each branch:

- A CSV file containing daily transaction data is generated.
- At 8pm, the data is uploaded onto software installed on premises.
- Business intelligence reports are generated using this data.

This setup is marred by a lack of scalability due to software limitations, and the lack of ability to generate store-wide reports. This makes the identification of trends difficult, leading to an inability to tap in to key company-wide business insights.

Therefore, the client enlisted the help of Generation's data engineers to build a scalable, automated solution that fulfills their requirements.


## Client Requirements

The client wants a fully scalable ETL pipeline able to handle large amounts of transactional data. The pipeline will aggregate the data collected daily from each branch and onto a central data warehouse. Then, business intelligence software will be used to generate business insights.  

## Installation


## Ways of Working
The project consists of five sprints, each with their own sprint goals. Each sprint lasted one week.

### Sprint 1

This sprint acts a 'proof-of-concept' sprint in which the pipeline is run locally, using a single CSV file to ensure the ETL script is functional. The data generated via the pipeline is then persisted to a Postgres instance in a Docker container.

#### ETL pipeline

In computing, extract, transform, load (ETL) is a three-phase process where data is extracted, transformed and loaded into an output data container. The data can be collated from one or more sources and it can also be outputted to one or more destinations. The steps taken to construct the ETL pipeline are detailed below.

**Extraction** 
```python
import os

import pandas as pd


def read_file(filename):
    if is_csv(filename) == True:
        try:
            content = pd.read_csv(filename, header=None)
            if content.empty:
                print('File is empty. Please try uploading another file.')
            else:
                content.columns = [
                    'date_time',
                    'branch',
                    'name',
                    'items',
                    'balance',
                    'payment_method',
                    'card_details',
                ]
            content = content.drop(['name', 'card_details'], axis=1)
            return content
        except FileNotFoundError:
            print(
                'Error: File not found in src directory. Please move your file to the src directory.'
            )
    else:
        print("Error: Incompatible file type. Please upload a '.csv' file.")
	

def is_csv(filename):
    extension = os.path.splitext(filename)[1]
    if extension == '.csv':
        return True
    else:
        False
```
The `read_csv()` function uses the pandas library to read the file's contents. Eception handling is used to ensure that the file exists in the same directory ("src"), that the file is not empty. It is used in conjuction with the `is_csv()` function that ensures the file is a csv file.


**Transformation** 
After extracting the data into a data frame we implemented some techniques on data according to our requirements. We removed personally identifiable information from data and any raw columns from the data and modified it according to the schema which is designed by following the normalization rules.

**Loading** 
Finally, we loaded that modified and arranged data into the database. we created the queries for creating databases and tables according to the database schema and loaded it into it. We used PostgreSQL for creating the databases and loading data.


## GitHub Actions

We also took some time in this sprint to set up some of the infrastructure of our project. One of the main tools used to help automate some of the process of our software development is GitHub Actions. It is a continuous integration/continuous deployment (CI/CD) tool. CI/CD is a DevOps practice, that automates certain tasks, that ensure code quality and consistency, that previously were done  manually.

GitHub Actions involves the setup of workflows that run *jobs* upon an *event* occurring in our repository.
A workflow is defined by a YAML file that contains a lists of tasks to be completed on our software after a trigger event. These jobs are run on virtual machines provided by GitHub. These jobs involve the use of linting tools and testing frameworks to ensure that new code is consistent and compatible with existing code. We set up our workflow such that it is triggered upon a pull request being merged to our main branch. Upon a pull request:

- Python is installed and set up on a virtual Ubuntu machine.
- Dependencies are installed via pip:
	- flake8
	- pytest
- Linting checks are performed with flake8.
- All existing tests are run on this new code using pytest.

If any of the checks fail the entire run fails and the developer must go back and check their code to make sure there are no errors or inconsistencies. One issue regarding pytest is that the run fails if no tests are found. As a temporary solution, a dummy test was created to prevent it causing failed runs.

A history of all runs are visible in the *Actions* tab within the repository.


## Data normalisation

Before we could load our data to the database, data normalisation steps were taken. Data normalisation is the process of structuring data so that it is cohesive across all records and fields. It also protects against certain anomalies that can occur, especially when working with large, evolving data sets. The following anomalies can be present when working with data in a RDBMS:

**Update anomalies**:

Update anomalies occur due to redundant data. If records containing such data are only partially updated, due to the user being unaware that the data is stored redundantly, the data becomes inconsistent. Let's take the example of data held on managers at a company. Let's say that a manager managed more than one department, and this was reflected by having the manager information almost completely duplicated (bar management division) over 2 rows. Updating something like a typo in the manager's name would have to occur twice in order for the data to be consistent. A lack of awareness as to the way the data is held could lead to only an update of a single record.

**Deletion anomalies**:

This refers to the unwanted loss of data due to deleting other data. An example of this would be if student data is held in a table along data regarding their teachers. If all the students taught by a certain teacher were removed, all records of that teacher would also be deleted. This happens due to how the student and teacher data is intertwined.

**Insertion anomalies**:

Insertion anomalies happen when records cannot be added to a database due to missing information. An example of this is the inability to add a sale of a customer that is not on file because a customer id must not be null.

The process of normalisation is the restructuring of data following a set number of 'normal forms'. A normal form refers to a standard of normalisation to adhere in order for the data to be normalised to the level of that standard. There exist five normal forms to which data can be normalised to. Below, the first three normal forms will be detailed, as well as snapshots of the data at each of these normal forms, as well as its original condition.

**Original data**

After removing columns containing PII, and naming the columns, a sample of the raw dataframe is shown below:

| Date time | Branch | Transaction | Total | Payment method |
|----------|------------|------|----------|------------|
| 25/08/2021 09:00 | Chesterfield | Regular Flavoured iced latte - Hazelnut - 2.75, Large Latte - 2.45 | 5.2 | CARD |

The datetime column isn't aligned with the Postgres TIMESTAMP data type, and multiple items are held in the Order field. This is remedied using the built-in `datetime` library. Data held like this would be very difficult to query, and therefore offers very little value to the client.

**First Normal Form (1NF):**

Rules:
- Each field should contain a single value
- Each record should be unique

This is the first stage of the normalisation process and was done by splitting each item in a transaction into a single record per item ordered. We decided to call this an 'order'

| Date time | Branch | Order| Item Price | Order total | Payment method |
|----------|------------|------|----------|------------|---------|
| 2021/08/25 09:00 | Chesterfield | Regular Flavoured iced latte - Hazelnut | 2.75 | 5.2 | CARD |
| 2021/08/25 09:00 | Chesterfield | Large Latte | 2.45 | 5.2 | CARD |

This data still has some redundancies as the values under the Branch and Order total columns are repeated for the same transaction over several rows. If there was an error in this column, not updating each record would lead to insertion anomalies.

**Second Normal Form (2NF):** 

Rules:
- Satisfies 1NF.
- No transitive dependencies - all non-prime attributes are fully dependent on the primary key. 

|Transaction id| Date time | Branch | Order| Item Price | Order total | Payment method |
|--|----------|------------|------|----------|------------|---------|
|1| 25/08/2021 09:00 | Chesterfield | Regular Flavoured iced latte - Hazelnut | 2.75 | 5.2 | CARD |
|1 |25/08/2021 09:00 | Chesterfield | Large Latte | 2.45 | 5.2 | CARD |

In this modified schema each record can be identified by its transaction id, making this the primary. Because the primary key is a single column, all columns are fully functionally dependent on the primary key.  However, the primary key should be able to identify a single record. This cannot happen as it is repeated over multiple records.

The potential issues surrounding update anomalies are not rectified by adhering to second normal form so further normalisation steps are required, to tackle both the issues with the primary key and the transitive dependencies .

   
**Third Normal Form (3NF):**

Rules:
- Satisfies 2NF.
- There are no transitive dependencies (a non-prime attribute depending on another non-prime attribute).

The following tables were made to adhere to to 3NF.

 Transactions:
| Transaction id | Date time | Branch id |  Payment amount | Payment method |
|-----|----|-----|-----|----|
| 1 | 25/08/2021 09:00 | 1 | 5.2 | CARD | 

Orders:
| Order id | Name | Order price | 
|---|---|---|
| 1 | Regular Flavoured iced latte - Hazelnut | 2.75 |

Branch:
| Branch id | Branch name |
|---|---|
| 1 | Chesterfield |

In the 2NF table, the order price is dependent on the order, so by separating the relations into a transaction and order table, those transitive dependencies are removed. Also, the removal of data referring to orders and referencing them via an order id allows for a unique primary key. The removal of the branch name into a separate table allows for a reduction in update anomalies. The same could also be applied to the 

Furthermore, seeing as an order is a single product that makes up a transaction, any products provided by the business that have not been bought by any customers would not be viewable on the database. Therefore, another table was created to reflect the client's  need to view if any products are not selling well.

Products:
| Product id | Product name | Product price | Product size | 
|---|---|---|---|
| 1 | Latte | 2.15 | Regular |

Some inconsistencies still exist in the way we've structured the data, namely the repetition of product name in the order table, as well as how it is referenced (a single order field includes both the product name and size), in comparison to how products are referenced in the product table. Our group's focus was on delivering an MVP that works within the time limit given to us. We decided further alterations would be done in later sprints.

## Docker

For sprint one we were required to make a docker container storing our postgres database. For this we created a docker compose file which had the latest version and all the key information about the container. For example username and password to access the database which would be important when trying to form a connection with python. In our container we also decided to add another image called adminer as a user interface for a better visualisation of our database. Putting all this information in a docker compose file is vital so that everyone in the team can create the same container with a simple docker compose up command. The only issue is that the docker container  is only accessible to its local host.

## CI/CD

CI/CD is an essential part of DevOps and any modern software development practice. A purpose-built CI/CD approach can maximize development time by improving an organization’s productivity, increasing efficiency, and streamlining workflows through built-in automation, testing, and collaboration.
 
Continuous integration is the practice of integrating all code changes into the main branch of a shared source code repository early and often, automatically testing each change when we commit or merge them, and automatically kicking off a build. With continuous integration, errors and security issues can be identified and fixed more easily, and much earlier in the development process.
Continuous delivery is a software development practice that works in conjunction with CI to automate the infrastructure provisioning and application release process.

```
.
├── .github
│   └── workflows
│       └── deploy.yml
	└── python-package.yml
```
```yaml
name: CI
on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]
```
This piece of code shows the name of the action and what particular task will be done in the main repository. So whenever new changes accrue in the main repository it runs all the tests and shows the results in the Actions tab.
```yaml
jobs:
  Deploy:
    name: Deploy to AWS
    runs-on: Ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1-node16
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-deploy-role
          aws-region: eu-west-1
          role-duration-seconds: 1200
      - name: Install AWS CLI
        run: sudo apt-get install awscli -y

      - name: Validate Cloudformation template
        run: aws cloudformation validate-template --template-body file://infra-template.yml

      - name: Update CloudFormation stack
        run: |aws cloudformation update-stack --stack-name alinewstack --template-body file://infra-template.yml --region eu-west-1
```	
In this code, we deployed our cloudformation file into AWS which will create the object method, instance and other necessary implementations inside the file. We have configured the AWS credential by adding the particular link and also assigned the GitHub to deploy role. This YAML file mainly connects with AWS and checks the validation of our cloud formation file and then updates the AWS stack which mainly deploys our piece of instruction in AWS.
          

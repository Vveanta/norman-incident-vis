# Datasheet for CIS6930, Spring 2024 Assignment 2 Dataset

## Motivation

- **Purpose**: This dataset was created to augment and enrich data extracted from public police department incident reports, with the specific goal of providing additional context (e.g., weather conditions, time of day) for each incident. This augmentation facilitates deeper analysis and allows for the exploration of patterns or correlations between incidents and these contextual factors.
- **Creators**: This dataset was created by Vedansh Maheshwari as part of the CIS6930 course at the University of Florida, specifically for the Spring 2024 Assignment 2 on Data Augmentation.
- **Funding**: The creation of this dataset was supported as part of the academic coursework at the University of Florida. No specific external funding was provided.
- **Comments**: N/A.

## Composition

- **Instances Represent**: Each instance represents an incident reported by the Norman Police Department, including details such as incident time, location, nature, and additional augmented data.
- **Instance Types**: There's only one type of instance - police incidents, with augmented data including weather conditions, time-related information, and geographical classifications.
- **Total Instances**: The total number of instances varies based on the number of incident reports available at the time of dataset creation.
- **Data Coverage**: The dataset is a non-random sample of incidents reported by the Norman Police Department. It is not necessarily representative of all incidents in the area but is intended to provide a snapshot for analysis.
- **Instance Data**: Each instance includes both raw data (the incident report details as in Incient DateTim, Incident Number, Incident Street Address,  Type fo Incident and incident ORI, ) and augmented data (weather conditions, geographical classification, etc.).
- **Labels**: Each instance includes labels such as weather condition codes and side of town classifications.
- **Missing Information**: There may be missing data due to unreported details in the original incident reports or due to limitations in the data augmentation process (e.g., unavailable historical weather data for certain dates).
- **Relationships**: Relationships between instances are not explicitly made, as each incident is treated independently.
- **Data Splits**: Not applicable; the dataset is intended for general analysis rather than model training and testing.
- **Errors/Noise**: Some level of noise and error may be present due to inaccuracies in the original incident reports or in the data augmentation sources (e.g., weather APIs).
- **External Resources**: The dataset relies on external resources for augmentation, such as historical weather data APIs. No guarantees are made about the constancy of these resources over time.
- **Confidential Data**: The dataset does not contain confidential information; it is derived from public incident reports and publicly available data sources.
- **Offensive Content**: Not applicable; the dataset focuses on incident reports and does not include directly offensive content.

## Collection Process

- **Acquisition**: Data associated with each instance was directly observable from public police incident reports in Norman, OK, USA and augmented through APIs for weather data and geocoding services.
- **Collection Mechanisms**: The data was collected manually through the analysis of public reports and programmatically via APIs for weather data and geocoding.
- **Timeframe**: The data collection timeframe matches the publication dates of the incident reports, with data augmentation processes conducted shortly thereafter.
- **Ethical Review**: Not applicable; the dataset was created as part of a coursework assignment and relies on publicly available data.

## Preprocessing/cleaning/labeling

- **Preprocessing**: Data cleaning and labeling involved geocoding incident locations, fetching historical weather data, and classifying incidents based on the time of day and geographical information.
- **Raw Data**: The "raw" incident report data was preserved alongside the augmented dataset to support unanticipated future uses.

## Uses

- **Previous Uses**: This dataset has been used primarily for educational purposes in the context of the CIS6930 course.
- **Potential Uses**: Beyond educational purposes, the dataset could be used for research into patterns of incidents in relation to weather conditions, times of day, and geographical locations.
- **Limitations for Future Uses**: Users should be aware of the potential biases introduced by the non-random sampling of incidents and the limitations of external data sources used for augmentation.

## Distribution

- **Distribution Method**: The dataset is intended to be distributed via GitHub, accompanying the course's educational materials.
- **Maintenance**: The dataset will be maintained by the course instructors for the duration of the CIS6930 course offering.
- **Contact**: Users can contact the course instructors via the University of Florida's Department of Computer Science for questions or support related to the dataset.

## Maintenance

- **Updates**: There are no plans for regular updates to the dataset, as it is intended as a static resource for educational use.
- **Versioning**: Older versions of the dataset will not be actively maintained or supported.
- **Contributions**: While there is no formal mechanism for external contributions to the dataset, users are encouraged to reach out to the course instructors with suggestions or augmentations.



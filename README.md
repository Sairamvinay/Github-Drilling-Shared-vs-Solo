# Github-Drilling-Shared-vs-Solo
### Team Members: 
Seongwoo Choi, Terry Guan, Sutej Kulkarni, Jinxiao (Jason) Song, Sairamvinay Vijayaraghavan

- Seongwoo Choi, Terry Guan, Sutej Kulkarni, Jason (Jinxiao) Song, and Sairamvinay Vijayaraghavan agree to participate and work on this project with the understanding of the project.

## Introduction
GitHub is a web-based open-source version control software that helps developers store and manage their code, as well as track and control changes to their code. In the world of software development, developers and users utilize GitHub as an issue tracker and code collaboration tool. It is critically important to understand that software development is very hard to achieve unless there is communication amongst developers. 

We can clearly see that communication and collaboration across developers improve the productivity of software developers within an open-source software medium. Therefore, it is important to collectively analyze the influence of software development procedures in terms of productivity as well as the size of software developer groups because industries analyze their productivity with their analytical skills and their performance metrics.

The goal of this paper is to investigate the correlation between shared development and productivity on Github. Specifically, we want to find the critical features that are correlated with communication across developers and influence the issue closure latency.


## Research Questions and Hypothesis
### Research and practice of software development are performed under various assumptions, their relationship with hypotheses, and discovered facts for validation. Based on the extensive empirical studies we have investigated, we have constructed several hypotheses for this research:

- **Research Question I**: In general, we know that more people working on development can improve productivity. Hence, we want to discover whether in open source software development: In an OSS medium, we can observe in general that more people working on development tends to improve productivity (by solving the proposed problems faster), but will this trend persist whenever there are more people working on the same project. We seek to answer whether for any project: With a larger software development team (more developers working on the same project), is there effectively a lower issue closure latency in open source projects? 

- **Research Question II**: In terms of one project’s productivity, would the presence of more shared developers reduce the issue closure latency? For the research purpose of this project, we consider shared developers as those who have contributed to multiple projects other than the current working project during the current project’s age time frame. 

- **Research Question III**: We analyze whether the project’s average latency of issue closure time reduces when the number of developers communicates knowledge across projects in terms of sharing knowledge? We consider this since we firmly believe that working on multiple projects would facilitate the transfer of knowledge across developers and improve the productivity of a software development team.

- **Hypothesis I**: An increase in the number of developers working on the same project (team size) can lead to lower latency in resolving issues

- **Hypothesis II**: An increase in the number of shared developers indicates more communication and collaboration between them, which leads to lower latency in resolving issues

- **Hypothesis III**: The project’s average latency of issue closure time can be reduced due to having developers that communicate knowledge across projects in terms of sharing knowledge.

Based on the research questions, we attempt to validate our hypothesis on the role of communication during software development. 

## Repository Contents
In this repository, we have committed and worked on several programming projects to conduct our research project. 
Every content has its own purpose that is linked to other files. Every file is free to view, and edit for further research purposes. Refer to Python scripts that are written using Google Colab + Jupyter Notebooks for better understanding of methodology. 

## Methodologies
For our project, we chose quantitative analysis since we were primarily analyzing data with numeric values and we wanted to derive conclusions from our data by statistical modeling techniques. We improved the number of samples by collecting more data by crawling the GitHub-based APIs. For the inputs, we decided to use the project size, the team size (number of contributors), total closed issues, the average number of cross-development repositories by a contributor for each repository, the average comments, project age, and the number of forks as the independent variables(features).

## Data
We gathered GitHub’s top 50 projects each day as returned by the search API, which allowed us to collect 12,800 samples initially. We filtered our search then to identify just those repositories with at least one closed issue and obtained around 10381 samples before processing.

## Results
There are many outliers in our data and all our features did not possess a perfect Gaussian distribution but the average number of comments. For the outlier detection, we performed a simple outlier removal technique entirely based on the percentile values of the features. We calculated the 97.5th percentile of each of the features we collected and removed values larger than the 97.5th percentile by using these as a cutoff to remove the outlier samples. We also calculated the 2.5th percentile of our entire dataset which was leveraged as a cutoff for removing those samples which have feature values that are lesser than its 2.5th percentile. After outlier detection, we had a final dataset of 6757 samples.

## Final Report
Use this [link](https://drive.google.com/file/d/1TRELrJ8Hwhl3UI0O8HaQ5j12RUmcA8hp/view?usp=sharing) to visit Google Doc for detailed proposal of the project. 


## Link to Project Proposal
Use this [link](https://docs.google.com/document/d/1rW-i0BhQkm2TUJ87Rs1wZ_mWxzvZEWk6vASmrXw_kJM/edit?usp=sharing) to visit Google Doc for detailed proposal of the project. 


## Link to Progress Report
Use this [link](https://docs.google.com/document/d/1SnCGZZId4t1AHfkppjk1gO1tNbS_FJuzwy9lyC_tc_Y/edit?usp=sharing) to visit Google Doc for detailed overview/progress of the project. 

> This project is entitled to Seongwoo Choi, Terry Guan, Sutej Kulkarni, Jinxiao (Jason) Song, Sairamvinay Vijayaraghavan

ECS 260: Software Engineering Fall 2021  @The University of California, Davis
![](https://www.google.com/url?sa=i&url=https%3A%2F%2Fworldvectorlogo.com%2Flogo%2Fuc-davis&psig=AOvVaw3qubUieRqzJPtgU6fhDy1Y&ust=1639075262069000&source=images&cd=vfe&ved=0CAsQjRxqFwoTCOiEgKjt1PQCFQAAAAAdAAAAABAJ)
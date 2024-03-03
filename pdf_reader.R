# install.packages("pdftools")
# install.packages("tidyverse")
# install.packages("lubridate")
# install.packages("dplyr")
# install.packages("stringr")
# install.packages("jsonlite")
library(pdftools)
library(tidyverse)
library(lubridate)
library(dplyr)
library(stringr)
library(jsonlite)

## rm(list = ls())
# remember to setwd()
# setwd("../Bucky-Boo-Final/")


source("pdf_reader_functions.R")

filepath_json = "all_courses.json"
course_json = fromJSON(filepath_json) %>% 
  as.data.frame() %>% 
  summarize(title, credits)

michael = "Michael_DEGREE_PLAN.pdf"
michael2 = "Michael_DEGREE_PLAN_2.pdf"
shrey = "Shrey_DEGREE_PLAN.pdf"
cam = "Cam_DEGREE_PLAN.pdf"
zamzam = "Zamzam_DEGREE_PLAN.pdf"

# user uploaded file will replace filepath
filepath = shrey

text = read_pdf(filepath)
major_degree = get_major_degree(text)
# name = get_name(text)

courses = trim_text(text)

semesters = get_semesters(courses) %>%split_semesters()

valid_sems = validate_semesters(semesters, courses)

sem_pos = semester_pos(courses)

df = read_courses(valid_sems, courses, course_json) 

write.csv(x=df, file=paste0(filepath,"_courses.csv"))

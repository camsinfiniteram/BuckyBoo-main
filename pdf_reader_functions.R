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

# reads pdf document and splits pdf text into separate rows in a 2D-List
read_pdf <- function(filepath) {
  text = pdf_text(filepath) %>% str_split("\n")
  return(text)
}

# gets name of person who uploaded the pdf
# here in case, in the future, this project decides to implement an
#   accounts/userbase system
get_name <- function(list_2d) {
  ret_name = str_extract(list_2d[[1]][1], "for (.+)$")
  return(substr(ret_name, 5, str_length(ret_name)))
}

# gets the major and degree
get_major_degree <- function(list_2d) {
  ret_line = list_2d[[1]][3]
  return(str_squish(substr(ret_line, 16, 100)))
}

# trims excess text in list_2d by getting rid of the headers and footers
trim_text <- function(list_2d) {
  for(i in seq_along(list_2d)) {
    if (i == 1) {
      list_2d[[i]] <- list_2d[[i]][-1:-6]
    } else {
      list_2d[[i]] <- list_2d[[i]][-1:-5]
    }
    page_length <- length(list_2d[[i]])
    footer <- page_length-5
    list_2d[[i]] <- list_2d[[i]][-footer:-page_length]
  }
  return(list_2d)
}

# finds where, in the same list element, a new academic year begins
#   (in the pdf file0)
newline_index <- function(list) {
  for (i in seq_along(list)) {
    for (line in seq_along(list[[i]][-length(list)])) {
      if (list[[i]][line] == "" & list[[i]][line+1] == "") {
        return(as.numeric(line+2))
      }
    }
  }
}

# gets a vector of semesters (does not split them... yet!)
get_semesters <- function(list) {
  ret = c()
  for (i in seq_along(list)) {
    sublist <- list[[i]]
    for (line in seq_along(sublist)) {
      if (line == 1 || line == newline_index(list)) {
        ret = c(ret, str_squish(sublist[line]))
      }
    }
  }
  return(ret)
}

# splits the year into its respective semesters
split_semesters <- function(list) {
  temp = c()
  ret = c()

  temp = gsub("(Fall|Spring|Summer) (\\d{4})", "\\1, \\2", list, perl=TRUE)
  ret = c(ret, str_split(temp, ","))
  
  return(ret)
}

get_group <- function(list) {
  ret = c()
  for (i in seq_along(list)) {
    sublist <- list[[i]]
    for (line in seq_along(sublist)) {
      if (line == 3 || line == (newline_index(list)+2)) {
        ret = c(ret, str_count(sublist[line], "Grade"))
      }
    }
  }
  return(ret)
}

# validates if the found semesters actually had enrolled classes or not
validate_semesters <- function(sems_list_2d, courses_list_2d) {
  num_grades = c()
  num_grades = c(num_grades, get_group(courses_list_2d))
  return(num_grades)
}

# lookup function to see if a course exists in the json_file
check_json <- function(lookup, json_file) {
  if(is.data.frame(json_file)) {
    for (i in seq_len(nrow(json_file))) {
      if (json_file$title[i] == lookup) { 
        return(i)
      }
    }
  } else if(is.list(json_file)) {
  }
  return("ignore")
}

semester_pos <- function(courses) {
  sem_pos = c()
  for (level in seq_along(courses)) {
    sublist <- courses[[level]]
    str_loc <- str_locate_all(sublist, "\\d{4} [A-Za-z]{1,6}")
    #print(length(sem_pos[[level]][1,]))
  }
  return(sem_pos)
}

# pieces together everything into one dataframe from the pdfs
read_courses <- function(valid_sems, courses, json_file, start_index=3) {
  # Initialize an empty data frame with specified columns
  # ret <- data.frame(title=character(), year=integer(), semester=character(), stringsAsFactors=FALSE)
  ret <- data.frame(title=character(), credits=character(), year=integer(), semester=character())
  
  for (level in seq_along(courses)) {
    sublist <- courses[[level]]
    for (iter in seq_along(valid_sems[[level]])) {
      #print(iter)
      year_in = NA
      semester_in = NA
      
      for (i in seq_along(sublist)) {
        index1 = start_index
        index2 = start_index+20
        #print(paste(index1, index2))
        substringi = substr(sublist[i], index1, index2)
        subsquish = str_squish(substringi)
        
        if (str_detect(subsquish, "(Fall|Spring|Summer)")) {
          year_in = as.numeric(substr(subsquish, 1, 4))
          #print(year_in)
          semester_in = substr(subsquish, 6, str_length(subsquish))
          print(semester_in)
        }
        
        # only for title
        #print(subsquish)
        
        if ( (any(json_file$title == subsquish))) {
          
          df_cr_ind = which(json_file$title == subsquish)
          new_row <- data.frame(title=subsquish, credits=json_file$credits[df_cr_ind], 
                                year=year_in, semester=semester_in)
          ret <- rbind(ret, new_row)
        } else if (!(str_detect(subsquish, "(Subject|Catalog)|(Fall|Spring|Summer)")) 
                   & (str_length(subsquish) > 0)) {
          new_row <- data.frame(title=subsquish, credits=NA, year=year_in, 
                                semester=semester_in)
          ret <- rbind(ret, new_row)
        }
      }
    }
  }
  return(ret)
}


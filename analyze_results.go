package main

import (
	"encoding/csv"
	"fmt"
	"io"
	"os"
	"strconv"
)

type Options map[string]int
type Subjects map[string]Options
type Instances map[string]Subjects

var dataset map[string]Instances

func addToDataset(record []string) {
	entity := record[0]
	instance := record[1]
	subject := record[2]
	option := record[3]
	score, _ := strconv.Atoi(record[4])

	_, ok := dataset[entity]
	if !ok {
		dataset[entity] = make(map[string]Subjects)
	}
	_, ok = dataset[entity][instance]
	if !ok {
		dataset[entity][instance] = make(map[string]Options)
	}
	_, ok = dataset[entity][instance][subject]
	if !ok {
		dataset[entity][instance][subject] = make(map[string]int)
	}

	dataset[entity][instance][subject][option] = score
}

func getDist(options_1, options_2 Options) int {
	dist := 0
	for option, score := range options_1 {
	    if score > options_2[option] {
	        dist = dist + score - options_2[option]
	    } else {
	        dist = dist + options_2[option] - score
	    }
	}
	dist = dist / 2
	return dist
}

func findNearest(subjects Subjects, subject string) string {
	_, ok := subjects[subject]
	if !ok {
		return ""
	}
	nearest_dist := 100
	nearest := ""
	for s, options := range subjects {
		if s != subject {
			current_dist := getDist(options, subjects[subject])
			if current_dist < nearest_dist {
				nearest_dist = current_dist
				nearest = s
			}
		}
	}
	return nearest
}

func main() {
	dataset = make(map[string]Instances)

	file, err := os.Open("cvpr_db_results.csv")
	if err != nil {
		fmt.Println("Error: ", err)
		return
	}
	defer file.Close()
	reader := csv.NewReader(file)
	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		} else if err != nil {
			fmt.Println("Error: ", err)
			return
		}
		addToDataset(record)
	}

	// known_subjects := []string{"ACTION", "FLUENT", "COMPUTER", "COMPUTER_DURATION"}
	known_subjects := []string{"causalgrammar"}

	for entity, instances := range dataset {
		for instance, subjects := range instances {
			for _, known_subject := range known_subjects {
				_, ok := subjects[known_subject]
				if !ok {
					fmt.Println("*** KNOWN SUBJECT ", known_subject, " NOT KNOWN FOR INSTANCE ", instance)
					continue
				}
				nearest_subject := findNearest(subjects, known_subject)
				if nearest_subject != "" {
					fmt.Println("Entity:", entity, "Instance:", instance, known_subject, "\b:", subjects[known_subject], "NearestHuman:", subjects[nearest_subject])
				} else {
					fmt.Println("--- Entity:", entity, "Instance:", instance, known_subject, "\b: NOT FOUND")
					fmt.Println("---- Known:", subjects[known_subject])
					fmt.Println("----   All:", subjects)
				}
			}
		}
	}
}

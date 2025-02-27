/*
Copyright 2023 IBM Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package complytime 

import (
	"bytes"
	"embed"
	"fmt"
	"html/template"
	"os"
	"strings"

	// "go.uber.org/zap"

	"github.com/oscal-compass/compliance-to-policy-go/v2/pkg/oscal"
	oscalTypes "github.com/defenseunicorns/go-oscal/src/types/oscal-1-1-2"
	tp "github.com/oscal-compass/compliance-to-policy-go/v2/pkg/pvpcommon/template"
	typecommon "github.com/oscal-compass/compliance-to-policy-go/v2/pkg/types/oscal/common"
)

//go:embed template/*.md
var embeddedResources embed.FS

type Oscal2Posture struct {
	assessmentResults oscalTypes.AssessmentResults 
	templateFile      *string
}

type TemplateValues struct {
	CatalogTitle     string
	Components       oscalTypes.ComponentDefinition
	AssessmentResult oscalTypes.AssessmentResults
}

func NewOscal2Posture(assessmentResults oscalTypes.AssessmentResults, templateFile *string) *Oscal2Posture {
	return &Oscal2Posture{
		assessmentResults: assessmentResults,
		templateFile:      templateFile,
	}
}

func (r *Oscal2Posture) findSubjects(ruleId string) []oscalTypes.AssessmentSubject {
	subjects := []oscalTypes.AssessmentSubject{}
	for _, r := range r.assessmentResults.Results {
		for _, ob := range *r.Observations {
			properties := []typecommon.Prop{}
			for _, p := range *ob.Props {
				// Here convert the prop in oscal-1-1-2 to c2p props
				property := &typecommon.Prop{
					Name: p.Name,
					Ns: p.Ns,
					Value: p.Value,
					Class: p.Class,
					Remarks: p.Remarks,
				}
				properties = append(properties, *property)
			}
			prop, found := oscal.FindProp("assessment-rule-id", properties)
			fmt.Printf("prop value -  %s\n", prop.Value)
			if found && prop.Value == ruleId {
//				subjects = append(subjects, *ob.Subjects...)
				fmt.Printf("prop value is the ruleid  %s\n", ruleId)
			}
		}
	}
	return subjects
}

func (r *Oscal2Posture) toTemplateValue() tp.TemplateValue {
	templateValue := tp.TemplateValue{
		// CatalogTitle: r.c2pParsed.Catalog.Catalog.Metadata.Title,
		CatalogTitle: "REPLACE ME", 
		Components:   []tp.Component{},
	}
//	for _, componentObject := range r.c2pParsed.ComponentObjects {
//		if componentObject.ComponentType == "validation" {
//			continue
//		}
//		component := tp.Component{
//			ComponentTitle: componentObject.ComponentTitle,
//			ControlResults: []tp.ControlResult{},
//		}
//		for _, cio := range componentObject.ControlImpleObjects {
//			for _, co := range cio.ControlObjects {
//				controlResult := tp.ControlResult{
//					ControlId:   co.GetControlId(),
//					RuleResults: []tp.RuleResult{},
//				}
//				for _, ruleId := range co.RuleIds {
//					subjects := []tp.Subject{}
//					rawSubjects := r.findSubjects(ruleId)
//					for _, rawSubject := range rawSubjects {
//						var result, reason string
//						resultProp, resultFound := oscal.FindProp("result", rawSubject.Props)
//						reasonProp, reasonFound := oscal.FindProp("reason", rawSubject.Props)
//
//						if resultFound {
//							result = resultProp.Value
//							if reasonFound {
//								reason = reasonProp.Value
//							}
//						} else {
//							result = "Error"
//							reason = "No results found."
//						}
//						subject := tp.Subject{
//							Title:  rawSubject.Title,
//							UUID:   rawSubject.SubjectUUID,
//							Result: result,
//							Reason: reason,
//						}
//						subjects = append(subjects, subject)
//					}
//					controlResult.RuleResults = append(controlResult.RuleResults, tp.RuleResult{
//						RuleId:   ruleId,
//						Subjects: subjects,
//					})
//				}
//				component.ControlResults = append(component.ControlResults, controlResult)
//			}
//		}
//		templateValue.Components = append(templateValue.Components, component)
//	}
	return templateValue
}

func (r *Oscal2Posture) Generate() ([]byte, error) {
	var templateData []byte
	var err error
	if r.templateFile == nil {
		templateData, err = embeddedResources.ReadFile("template/template.md")
	} else {
		templateData, err = os.ReadFile(*r.templateFile)
	}
	if err != nil {
		return nil, err
	}

	funcmap := template.FuncMap{
		"newline_with_indent": func(text string, indent int) string {
			newText := strings.ReplaceAll(text, "\n", "\n"+strings.Repeat(" ", indent))
			return newText
		},
	}

	templateString := string(templateData)
	tmpl := template.New("report.md")
	tmpl.Funcs(funcmap)
	tmpl, err = tmpl.Parse(templateString)
	fmt.Printf("tmpl %s\n", tmpl)
	fmt.Printf("tmpl err %s\n", err)

	if err != nil {
		return nil, err
	}
	templateValue := r.toTemplateValue()
	buffer := bytes.NewBuffer([]byte{})
	err = tmpl.Execute(buffer, templateValue)
	if err != nil {
		return nil, err
	}
	return buffer.Bytes(), nil
}

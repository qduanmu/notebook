// SPDX-License-Identifier: Apache-2.0

package complytime

import (
	"fmt"
	"encoding/json"
	"os"
	"path"

	oscalTypes "github.com/defenseunicorns/go-oscal/src/types/oscal-1-1-2"
	// "github.com/oscal-compass/compliance-to-policy-go/v2/pkg"
	// "github.com/oscal-compass/compliance-to-policy-go/v2/pkg/kyverno"
	// "github.com/oscal-compass/compliance-to-policy-go/v2/pkg/pvpcommon"
	// typec2pcr "github.com/oscal-compass/compliance-to-policy-go/v2/pkg/types/c2pcr"
)

// WriteAssessmentResults writes AssessmentResults as a JSON file to a given path location.
func WriteAssessmentResults(assessmentResults *oscalTypes.AssessmentResults, assessmentResultsLocation string) error {

	oscalModels := oscalTypes.OscalModels{
		AssessmentResults: assessmentResults,
	}
	fileExt := path.Ext(assessmentResultsLocation)
	fmt.Printf("Assessment results format %s\n", fileExt)
	fmt.Printf("oscalModels %s\n", oscalModels)
	if fileExt == ".json" {
		assessmentResultsJson, err := json.MarshalIndent(oscalModels, "", " ")
		if err != nil {
			return err
		}
		return os.WriteFile(assessmentResultsLocation, assessmentResultsJson, 0600)
	}

	if fileExt == ".md" {
		// r := NewOscal2Posture(oscalModels, nil)
		r := NewOscal2Posture(*assessmentResults, nil)
		_, err := r.Generate()
		if err != nil {
		        return err
		}
	}

	return nil
}


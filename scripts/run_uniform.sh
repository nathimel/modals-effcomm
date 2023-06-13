echo "./scripts/run_full_experiment.sh configs/journal/half_credit_literal.yml"
./scripts/run_full_experiment.sh configs/journal/half_credit_literal.yml > outputs/journal/half_credit_literal/system_output.txt

echo "./scripts/run_full_experiment.sh configs/journal/indicator_literal.yml"
./scripts/run_full_experiment.sh configs/journal/indicator_literal.yml > outputs/journal/indicator_literal/system_output.txt

echo "./scripts/run_full_experiment.sh configs/journal/half_credit_pragmatic.yml"
./scripts/run_full_experiment.sh configs/journal/half_credit_pragmatic.yml > outputs/journal/half_credit_pragmatic/system_output.txt

echo "./scripts/run_full_experiment.sh configs/journal/indicator_pragmatic.yml"
./scripts/run_full_experiment.sh configs/journal/indicator_pragmatic.yml > outputs/journal/indicator_pragmatic/system_output.txt

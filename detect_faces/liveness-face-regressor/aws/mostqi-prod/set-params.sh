
#!/usr/bin/env bash

# Stop on any error         
set -e          

aws ssm put-parameter --overwrite --name "/services/liveness-fr/network-stack-name"                                    --type String                             --value "net-prod"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/cluster-stack-name"                                    --type String                             --value "cluster-prod"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/backbone-stack-name"                                   --type String                             --value "bb-prod"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/sns-errors-stack-name"                                 --type String                             --value "sns-errors-prod"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/environment-name"                                      --type String                             --value "Production"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/image-uri"                                             --type String                             --value "1"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/elastic-apm-secret-arn"                                --type String                             --value "arn:aws:secretsmanager:us-east-1:959869551280:secret:elastic-apm-secret-token-95hTLN"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/cloud-watch-logs-prefix"                               --type String                             --value "NONE"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/replica-min"                                           --type String                             --value "6"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/replica-max"                                           --type String                             --value "12"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/replica-desired"                                       --type String                             --value "6"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/elastic-kibana-log-writer-uri-arn"                     --type String                             --value "arn:aws:secretsmanager:us-east-1:959869551280:secret:elastic-kibana-log-writer-uri-aAiVLG"


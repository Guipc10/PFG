#!/usr/bin/env bash

# Stop on any error
set -e

aws ssm put-parameter --overwrite --name "/services/liveness-fr/network-stack-name"                                    --type String                             --value "net-dev"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/cluster-stack-name"                                    --type String                             --value "cluster-dev"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/backbone-stack-name"                                   --type String                             --value "bb-dev"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/sns-errors-stack-name"                                 --type String                             --value "sns-errors-dev"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/environment-name"                                      --type String                             --value "Development"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/image-uri"                                             --type String                             --value "420543937728.dkr.ecr.us-east-1.amazonaws.com/dev/liveness-fr:b6f8b273"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/elastic-apm-secret-arn"                                --type String                             --value "arn:aws:secretsmanager:us-east-1:420543937728:secret:elastic-apm-secret-token-Z9zcpe"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/cloud-watch-logs-prefix"                               --type String                             --value "NONE"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/replica-min"                                           --type String                             --value "4"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/replica-max"                                           --type String                             --value "7"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/replica-desired"                                       --type String                             --value "4"
aws ssm put-parameter --overwrite --name "/services/liveness-fr/elastic-kibana-log-writer-uri-arn"                     --type String                             --value "arn:aws:secretsmanager:us-east-1:420543937728:secret:elastic-kibana-log-writer-uri-4bWvmg"


pipeline {

   agent {
         label 'Flexibees-STAG-API'
         }

   stages {

     stage ('Docker Deployment') {
       steps {
          echo "copying the latest file in Docker container"
          sh 'sudo docker cp . bed-stage-server:/usr/src/app'
             }
         }

     stage  ('python packages installation & migrate') {
       steps {
          echo "installing the packages from requirement.txt file"
          sh 'sudo docker exec bed-stage-server pip install -r requirements.txt'
          sh 'sudo docker exec bed-stage-server python manage.py collectstatic --noinput'
          sh 'sudo docker exec bed-stage-server python manage.py migrate'

             }
         }
     stage  ('Cron Remove') {
       steps {
          echo "removing crons in crontab"
          sh 'sudo docker exec bed-stage-server python manage.py crontab remove'
             }
         }
     stage  ('Cron addition ') {
       steps {
          echo "adding crons in crontab"
          sh 'sudo docker exec bed-stage-server python manage.py crontab add'
             }
         } 
     stage ('Restart Docker') {
       steps {
          echo "restarting the docker & cron service start"
          sh "sudo docker restart bed-stage-server bed-gun-stage-server bed-crm-stage-server"
          sh "sudo docker exec bed-stage-server bash /etc/init.d/cron start"

             }
         }
     }
}

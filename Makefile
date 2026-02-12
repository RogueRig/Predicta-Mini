.PHONY: dev install deploy-hosting deploy-backend deploy

# Install backend dependencies
install:
	cd backend && pip install -r requirements.txt

# Run backend development server
dev:
	cd backend && python app.py

# Deploy frontend to Firebase Hosting
deploy-hosting:
	firebase deploy --only hosting

# Build and deploy backend to Cloud Run
deploy-backend:
	gcloud run deploy predicta-mini-api \
		--source backend \
		--region us-central1 \
		--allow-unauthenticated \
		--set-env-vars-file .env

# Full deployment
deploy: deploy-backend deploy-hosting

# Run locally with production settings
prod:
	cd backend && gunicorn --bind 0.0.0.0:8080 --workers 2 "app:create_app()"

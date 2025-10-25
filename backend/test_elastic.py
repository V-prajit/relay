"""Test Elasticsearch connection and ELSER model."""
from app.config import config
from app.elastic.client import elastic_client


def test_connection():
    """Test Elasticsearch connection."""
    print("Testing Elasticsearch connection...")
    print(f"Endpoint: {config.ELASTIC_ENDPOINT}")

    try:
        if elastic_client.ping():
            print("✓ Connection successful!")
        else:
            print("✗ Connection failed (ping returned False)")
            return False

        try:
            info = elastic_client.info()
            print(f"✓ Cluster name: {info['cluster_name']}")
            print(f"✓ Elasticsearch version: {info['version']['number']}")
        except Exception as e:
            print(f"✓ Connected to Elasticsearch (info unavailable: {type(e).__name__})")

        try:
            stats = elastic_client.ml.get_trained_models_stats(
                model_id=".elser_model_2_linux-x86_64"
            )
            deployment_state = stats['trained_model_stats'][0]['deployment_stats']['state']
            print(f"✓ ELSER model state: {deployment_state}")

            if deployment_state != "started":
                print("⚠ ELSER model not started.")
                print("  Deploy with: POST _ml/trained_models/.elser_model_2_linux-x86_64/_deploy")
        except Exception as e:
            print(f"⚠ ELSER model not found: {e}")
            print("  Deploy with: POST _ml/trained_models/.elser_model_2_linux-x86_64/_deploy")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check ELASTIC_API_KEY in .env")
        print("2. Check ELASTIC_ENDPOINT in .env")
        print("3. Verify Elastic Cloud project is running")
        return False


if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)

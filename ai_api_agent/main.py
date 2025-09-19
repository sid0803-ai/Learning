from core.agent import APIAgent

def main():
    agent = APIAgent("endpoints.json")
    agent.run()

if __name__ == "__main__":
    main()

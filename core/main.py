import sys
from pathlib import Path

# Add project root to python path so we can resolve package imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.pipeline import ConversationPipeline

def main() -> None:
    """
    Main entry point for the Campus Guide Robot Phase 1 backend.
    Runs a continuous terminal input conversation loop.
    """
    print("==================================================")
    print("   CAMPUS GUIDE ROBOT - PHASE 1 CONVERSATION")
    print("==================================================")
    print("Type your questions below.")
    print("Type 'exit' or 'quit' to shutdown the robot.\n")

    try:
        # Initialize pipeline (config load -> Gemini Client -> TTS engine)
        pipeline = ConversationPipeline()
        print("\nRobot is ready. Start asking questions!\n")
        
        while True:
            # 1. Capture terminal input
            try:
                user_input = input("You: ")
            except EOFError:
                # Catch terminal EOF (Ctrl+D)
                break
                
            # 2. Check for exit request
            if user_input.strip().lower() in ['exit', 'quit']:
                print("\nShutting down pipeline. Goodbye!")
                break
                
            # 3. Feed input into processing pipeline
            pipeline.run_turn(user_input)
            print("-" * 50)

    except KeyboardInterrupt:
        print("\n\nRobot execution interrupted by user. Shutting down...")
    except Exception as e:
        print(f"\n[CRITICAL FAILURE] System crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

import Foundation

// This is a test script to simulate the app's functionality
func runHealthSyncTest() {
    print("Starting HealthSync Test...")

    // 1. Test the MockDataGenerator
    print("\n--- Testing Mock Data Generation ---")
    let entries = MockDataGenerator.createMockJournalEntries()
    print("Generated \(entries.count) mock journal entries")

    // 2. Test the weekly summary
    print("\n--- Testing Weekly Summary Generation ---")
    let weeklySummary = MockDataGenerator.createMockWeeklySummary() 
    print("Generated weekly summary with \(weeklySummary.highlightedPatterns.count) patterns")
    print("First pattern: \(weeklySummary.highlightedPatterns.first?.description ?? "None")")

    // 3. Test doctor visit summary
    print("\n--- Testing Doctor Visit Summary Generation ---")
    let doctorSummary = MockDataGenerator.createMockDoctorVisitSummary()
    print("Generated doctor visit summary with \(doctorSummary.keySymptoms.count) key symptoms")
    print("First symptom: \(doctorSummary.keySymptoms.first?.name ?? "None")")

    print("\nHealthSync Test Complete!")
}

// Run the test
runHealthSyncTest()

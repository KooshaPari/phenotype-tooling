import SwiftUI

struct ContentView: View {
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            JournalEntryView()
                .tabItem {
                    Label("Journal", systemImage: "square.and.pencil")
                }
                .tag(0)
            
            WeeklySummaryView()
                .tabItem {
                    Label("Weekly", systemImage: "chart.bar.xaxis")
                }
                .tag(1)
            
            PatternAnalysisView()
                .tabItem {
                    Label("Patterns", systemImage: "puzzlepiece")
                }
                .tag(2)
            
            DoctorVisitPrepView()
                .tabItem {
                    Label("Doctor Visit", systemImage: "stethoscope")
                }
                .tag(3)
        }
        .onAppear {
            // Request HealthKit authorization when the app launches
            requestHealthKitPermissions()
        }
    }
    
    private func requestHealthKitPermissions() {
        HealthKitService.shared.requestAuthorization { success, error in
            if success {
                print("HealthKit authorization successful")
            } else if let error = error {
                print("HealthKit authorization failed: \(error.localizedDescription)")
            }
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}

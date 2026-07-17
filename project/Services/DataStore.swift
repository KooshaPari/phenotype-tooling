import Foundation

class DataStore {
    static let shared = DataStore()
    
    private let journalEntriesKey = "journalEntries"
    private let weeklySummariesKey = "weeklySummaries"
    private let doctorVisitSummariesKey = "doctorVisitSummaries"
    
    // MARK: - Journal Entries
    
    func saveJournalEntry(_ entry: JournalEntry) {
        var entries = loadJournalEntries()
        entries.append(entry)
        save(entries, forKey: journalEntriesKey)
    }
    
    func loadJournalEntries() -> [JournalEntry] {
        guard let data = UserDefaults.standard.data(forKey: journalEntriesKey) else {
            // Return mock data if no saved entries exist
            return MockDataGenerator.createMockJournalEntries()
        }
        
        do {
            return try JSONDecoder().decode([JournalEntry].self, from: data)
        } catch {
            print("Error loading journal entries: \(error)")
            return []
        }
    }
    
    func updateJournalEntry(_ updatedEntry: JournalEntry) {
        var entries = loadJournalEntries()
        if let index = entries.firstIndex(where: { $0.id == updatedEntry.id }) {
            entries[index] = updatedEntry
            save(entries, forKey: journalEntriesKey)
        }
    }
    
    func deleteJournalEntry(_ id: UUID) {
        var entries = loadJournalEntries()
        entries.removeAll(where: { $0.id == id })
        save(entries, forKey: journalEntriesKey)
    }
    
    // MARK: - Weekly Summaries
    
    func saveWeeklySummary(_ summary: WeeklySummary) {
        var summaries = loadWeeklySummaries()
        summaries.append(summary)
        save(summaries, forKey: weeklySummariesKey)
    }
    
    func loadWeeklySummaries() -> [WeeklySummary] {
        guard let data = UserDefaults.standard.data(forKey: weeklySummariesKey) else {
            // Return mock data if no saved summaries exist
            return [MockDataGenerator.createMockWeeklySummary()]
        }
        
        do {
            return try JSONDecoder().decode([WeeklySummary].self, from: data)
        } catch {
            print("Error loading weekly summaries: \(error)")
            return []
        }
    }
    
    func getLatestWeeklySummary() -> WeeklySummary? {
        let summaries = loadWeeklySummaries()
        return summaries.sorted(by: { $0.endDate > $1.endDate }).first
    }
    
    // MARK: - Doctor Visit Summaries
    
    func saveDoctorVisitSummary(_ summary: DoctorVisitSummary) {
        var summaries = loadDoctorVisitSummaries()
        summaries.append(summary)
        save(summaries, forKey: doctorVisitSummariesKey)
    }
    
    func loadDoctorVisitSummaries() -> [DoctorVisitSummary] {
        guard let data = UserDefaults.standard.data(forKey: doctorVisitSummariesKey) else {
            // Return mock data if no saved summaries exist
            return [MockDataGenerator.createMockDoctorVisitSummary()]
        }
        
        do {
            return try JSONDecoder().decode([DoctorVisitSummary].self, from: data)
        } catch {
            print("Error loading doctor visit summaries: \(error)")
            return []
        }
    }
    
    func getLatestDoctorVisitSummary() -> DoctorVisitSummary? {
        let summaries = loadDoctorVisitSummaries()
        return summaries.sorted(by: { $0.endDate > $1.endDate }).first
    }
    
    // MARK: - Helper Methods
    
    private func save<T: Encodable>(_ items: T, forKey key: String) {
        do {
            let data = try JSONEncoder().encode(items)
            UserDefaults.standard.set(data, forKey: key)
        } catch {
            print("Error saving data: \(error)")
        }
    }
    
    // Get journal entries within a date range
    func getJournalEntries(from startDate: Date, to endDate: Date) -> [JournalEntry] {
        let entries = loadJournalEntries()
        return entries.filter { entry in
            return entry.date >= startDate && entry.date <= endDate
        }
    }
    
    // Get entries with a specific symptom
    func getEntriesWithSymptom(_ symptomName: String) -> [JournalEntry] {
        let entries = loadJournalEntries()
        return entries.filter { entry in
            return entry.symptoms.contains(where: { $0.name.lowercased() == symptomName.lowercased() })
        }
    }
}

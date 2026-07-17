import SwiftUI

struct JournalEntryView: View {
    @State private var mood: Int = 3
    @State private var energy: Int = 3
    @State private var selectedSymptoms: [Symptom] = []
    @State private var notes: String = ""
    @State private var tags: String = ""
    @State private var showingSymptomSheet = false
    @State private var isLoading = false
    @State private var showingSuccessAlert = false
    
    // Available symptoms for selection
    private let availableSymptoms = [
        "Headache",
        "Fatigue",
        "Nausea",
        "Dizziness",
        "Muscle Pain",
        "Joint Pain",
        "Digestive Issues",
        "Anxiety",
        "Low Mood"
    ]
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("How do you feel today?")) {
                    VStack(alignment: .leading) {
                        Text("Mood: \(mood)/5")
                        Slider(value: Binding(
                            get: { Double(mood) },
                            set: { mood = Int($0) }
                        ), in: 1...5, step: 1)
                    }
                    
                    VStack(alignment: .leading) {
                        Text("Energy: \(energy)/5")
                        Slider(value: Binding(
                            get: { Double(energy) },
                            set: { energy = Int($0) }
                        ), in: 1...5, step: 1)
                    }
                }
                
                Section(header: Text("Symptoms")) {
                    Button(action: {
                        showingSymptomSheet = true
                    }) {
                        HStack {
                            Text("Add Symptoms")
                            Spacer()
                            Image(systemName: "plus.circle")
                        }
                    }
                    
                    if !selectedSymptoms.isEmpty {
                        ForEach(selectedSymptoms) { symptom in
                            HStack {
                                Text(symptom.name)
                                Spacer()
                                Text("Severity: \(symptom.severity)/10")
                            }
                        }
                        .onDelete(perform: deleteSymptom)
                    }
                }
                
                Section(header: Text("Notes")) {
                    TextEditor(text: $notes)
                        .frame(minHeight: 100)
                }
                
                Section(header: Text("Tags (comma separated)")) {
                    TextField("e.g., stress, exercise, medication", text: $tags)
                }
                
                Section {
                    Button(action: saveEntry) {
                        if isLoading {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle())
                        } else {
                            Text("Save Entry")
                                .frame(maxWidth: .infinity)
                                .foregroundColor(.white)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(10)
                    .disabled(isLoading)
                }
            }
            .navigationTitle("Daily Journal")
            .sheet(isPresented: $showingSymptomSheet) {
                SymptomSelectionView(selectedSymptoms: $selectedSymptoms, availableSymptoms: availableSymptoms)
            }
            .alert(isPresented: $showingSuccessAlert) {
                Alert(
                    title: Text("Entry Saved"),
                    message: Text("Your journal entry has been saved successfully."),
                    dismissButton: .default(Text("OK"))
                )
            }
        }
    }
    
    private func deleteSymptom(at offsets: IndexSet) {
        selectedSymptoms.remove(atOffsets: offsets)
    }
    
    private func saveEntry() {
        isLoading = true
        
        // Create tag array from comma-separated string
        let tagArray = tags.split(separator: ",").map { String($0.trimmingCharacters(in: .whitespaces)) }
        
        // Create a new journal entry
        let newEntry = JournalEntry(
            date: Date(),
            mood: mood,
            energy: energy,
            symptoms: selectedSymptoms,
            notes: notes,
            tags: tagArray
        )
        
        // Simulate fetching health data
        HealthKitService.shared.fetchHealthData(for: Date()) { sleepHours, stepCount, activeCalories, restingHeartRate in
            // Update the entry with health data
            var updatedEntry = newEntry
            updatedEntry.sleepHours = sleepHours
            updatedEntry.stepCount = stepCount
            updatedEntry.activeCalories = activeCalories
            updatedEntry.restingHeartRate = restingHeartRate
            
            // Save the entry
            DataStore.shared.saveJournalEntry(updatedEntry)
            
            // Reset the form and show success alert
            DispatchQueue.main.async {
                resetForm()
                isLoading = false
                showingSuccessAlert = true
            }
        }
    }
    
    private func resetForm() {
        mood = 3
        energy = 3
        selectedSymptoms = []
        notes = ""
        tags = ""
    }
}

struct SymptomSelectionView: View {
    @Binding var selectedSymptoms: [Symptom]
    let availableSymptoms: [String]
    @State private var newSymptomName = ""
    @State private var symptomSeverity = 5
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Add a Symptom")) {
                    Picker("Symptom", selection: $newSymptomName) {
                        Text("Select a symptom").tag("")
                        ForEach(availableSymptoms, id: \.self) { symptom in
                            Text(symptom).tag(symptom)
                        }
                    }
                    
                    if !newSymptomName.isEmpty {
                        VStack(alignment: .leading) {
                            Text("Severity: \(symptomSeverity)/10")
                            Slider(value: Binding(
                                get: { Double(symptomSeverity) },
                                set: { symptomSeverity = Int($0) }
                            ), in: 1...10, step: 1)
                        }
                        
                        Button("Add Symptom") {
                            addSymptom()
                        }
                    }
                }
                
                if !selectedSymptoms.isEmpty {
                    Section(header: Text("Selected Symptoms")) {
                        ForEach(selectedSymptoms) { symptom in
                            HStack {
                                Text(symptom.name)
                                Spacer()
                                Text("Severity: \(symptom.severity)/10")
                            }
                        }
                    }
                }
            }
            .navigationTitle("Symptoms")
            .navigationBarItems(trailing: Button("Done") {
                presentationMode.wrappedValue.dismiss()
            })
        }
    }
    
    private func addSymptom() {
        guard !newSymptomName.isEmpty else { return }
        
        // Check if the symptom is already selected
        if !selectedSymptoms.contains(where: { $0.name == newSymptomName }) {
            let newSymptom = Symptom(
                name: newSymptomName,
                severity: symptomSeverity
            )
            selectedSymptoms.append(newSymptom)
        }
        
        // Reset the form
        newSymptomName = ""
        symptomSeverity = 5
    }
}

struct JournalEntryView_Previews: PreviewProvider {
    static var previews: some View {
        JournalEntryView()
    }
}

from abc import ABC, abstractmethod
from datetime import datetime

# --- 1. ABSTRACTION: THE BASE BLUEPRINT ---
class Bird(ABC):
    def __init__(self, flock_id, breed, age_days, initial_count):
        self.flock_id = flock_id
        self.breed = breed
        self.age_days = age_days
        self.initial_count = initial_count
        self.current_count = initial_count # Default to all alive at start
        self._mortality_count = 0  # Protected attribute

    @abstractmethod
    def calculate_productivity(self):
        """Forces subclasses to define their own success metrics"""
        pass

    def calculate_mortality(self):
        """Common logic for all bird types to track health"""
        if self.initial_count == 0: return 0.0
        lost = self.initial_count - self.current_count
        mortality_rate = (lost / self.initial_count) * 100
        return mortality_rate
    
    def get_vaccination_reminder(self):
        """Logic based on common poultry vaccination timelines"""
        if 7 <= self.age_days <= 9:
            return "DUE: Gumboro (1st Dose)"
        elif 14 <= self.age_days <= 16:
            return "DUE: Lasota (1st Dose)"
        elif 21 <= self.age_days <= 23:
            return "DUE: Gumboro (2nd Dose)"
        else:
            return "No vaccines due today."
        

    @classmethod
    def generate_flock_data(cls, arrival_date_str):
        """Utility to calculate age and format date for the ID"""
        try:
            arrival_date = datetime.strptime(arrival_date_str, "%Y-%m-%d")
            age_days = (datetime.now() - arrival_date).days
            return age_days, arrival_date_str
        except ValueError:
            print("Error: Date must be in YYYY-MM-DD format.")
            return None, None

# --- 2. INHERITANCE & POLYMORPHISM: BROILER ---
class Broiler(Bird):
    def __init__(self, flock_id, breed, age_days, initial_count, weight_kg=0.05, feed_kg=0):
        super().__init__(flock_id, breed, age_days, initial_count)
        self.__weight_kg = weight_kg  # Encapsulation
        self.__feed_kg = feed_kg

    @classmethod
    def create_broiler(cls, breed, arrival_date_str, count):
        age_days, date_part = cls.generate_flock_data(arrival_date_str)
        if age_days is not None:
            return cls(f"BL-{date_part}", breed, age_days, count)
        return None

    def calculate_productivity(self):
        m_rate = self.calculate_mortality()
        fcr = self.__feed_kg / self.__weight_kg if self.weight_kg > 0 else 0
        vaccine = self.get_vaccination_reminder()

        status = "Healthy"
        if m_rate > 5.0: status = "CRITICAL: High Mortality"
        elif fcr > 2.0: status = "WARNING: High FCR"

        return f"FCR: {fcr:.2f} | Mortality: {m_rate:.1f}% | Status: {status}"
        

    def update_data(self, weight, feed):
        self.__weight_kg = weight
        self.__feed_kg = feed

# --- 3. INHERITANCE & POLYMORPHISM: LAYER ---
class Layer(Bird):
    def __init__(self, flock_id, breed, age_days, initial_count, eggs_today=0):
        super().__init__(flock_id, breed, age_days, initial_count)
        self.eggs_today = eggs_today

    @classmethod
    def create_layer(cls, breed, arrival_date_str, count):
        age_days, date_part = cls.generate_flock_data(arrival_date_str)
        if age_days is not None:
            return cls(f"LY-{date_part}", breed, age_days, count)
        return None

    def calculate_productivity(self):
        m_rate = self.calculate_mortality()
        rate = (self.eggs_today / self.current_count) * 100 if self.current_count > 0 else 0
        vaccine = self.get_vaccination_reminder()
        
        status = "Optimal"
        if m_rate > 5.0: status = "CRITICAL: High Mortality"
        elif rate < 75: status = "WARNING: Low Yield"
            
        return f"Egg Rate: {rate:.1f}% | Mortality: {m_rate:.1f}% | Status: {status} | {vaccine}"

# --- 4. THE MANAGER ---
class PoultryFarm:
    def __init__(self, name):
        self.name = name
        self.flocks = []

    def add_flock(self, flock):
        if flock: 
            self.flocks.append(flock)
            # SUCCESS FEEDBACK
            print("\n" + "*"*40)
            print(f"SUCCESS: {flock.breed} flock ({flock.flock_id}) has been added!")
            print(f"Current Age: {flock.age_days} days.")
            print("*"*40)

    def get_flock_by_id(self, fid):
        """Finds a saved flock so the farmer doesn't have to re-enter breed/date"""
        for f in self.flocks:
            if f.flock_id == fid:
                return f
        return None

    def show_report(self):
        print(f"\n{'='*25} {self.name.upper()} MANAGEMENT REPORT {'='*25}")
        for f in self.flocks:
            print(f"ID: {f.flock_id} | Breed: {f.breed} | Age: {f.age_days} Days")
            print(f"   >>> {f.calculate_productivity()}")
        print("="*80)

# --- 4. COMPOSITION: THE MANAGEMENT SYSTEM ---
def main():
    print("Welcome to the Poultry Intelligence System")
    farm = PoultryFarm(input("Enter Farm Name: "))
    
    while True:
        print("\nMAIN MENU:")
        print("1. Register New Flock (Breed/Date)")
        print("2. Update Daily Data (Feed/Eggs/Deaths)")
        print("3. View Full Farm Report")
        print("4. Exit")
        choice = input("Select Option (1-4): ")

        if choice == '1':
            print("\n--- NEW FLOCK REGISTRATION ---")
            type_choice = input(" Select Type (1 for Broiler, 2 for Layer): ")
            breed = input("Enter Breed: ")
            date = input("Arrival Date (YYYY-MM-DD): ")
            count = int(input("Initial Bird Count: "))
            
            try:
                arrival_date = datetime.strptime(date, "%Y-%m-%d")
                age = (datetime.now() - arrival_date).days
                
                if type_choice == '1':
                    new_bird = Broiler(f"BL-{date}", breed, age, count)
                else:
                    new_bird = Layer(f"LY-{date}", breed, age, count)
                
                farm.add_flock(new_bird) # This triggers the success message
            except ValueError:
                print("\nERROR: Invalid date format. Please use YYYY-MM-DD.")

        elif choice == '2':
            fid = input("Enter the Flock ID to update (e.g., BL-2026-03-01): ")
            flock = farm.get_flock_by_id(fid)
            
            if flock:
                # Update deaths
                alive = int(input(f"How many birds are currently alive (out of {flock.initial_count})? "))
                flock.current_count = alive
                
                # Update type-specific data
                if isinstance(flock, Broiler):
                    flock.weight_kg = float(input("Update Total Weight (kg): "))
                    flock.feed_kg = float(input("Update Total Feed Consumed (kg): "))
                elif isinstance(flock, Layer):
                    flock.eggs_today = int(input("Update Eggs Collected Today: "))
                print("Data updated successfully!")
            else:
                print("Flock ID not found. Check the Report for correct IDs.")

        elif choice == '3':
            farm.show_report()
        elif choice == '4':
            print("System shutting down. Secure your birds and keep going!")
            print("You are doing great Farmer. Thank you")
            break

if __name__ == "__main__":
    main()
    
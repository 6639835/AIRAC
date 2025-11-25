"""
AIRAC (Aeronautical Information Regulation And Control) Cycle Calculator

Based on ICAO Doc 8126 - Aeronautical Information Services Manual.
AIRAC cycles are 28 days long and follow a fixed schedule.
"""

from datetime import date, timedelta
from typing import NamedTuple


class AIRACCycle(NamedTuple):
    """Represents an AIRAC cycle with its properties."""
    identifier: str      # Format: YYCC (e.g., "2513" for cycle 13 of 2025)
    year: int            # Full year (e.g., 2025)
    ordinal: int         # Cycle number within the year (1-14)
    effective_date: date # Start date of the cycle
    expiration_date: date # End date of the cycle (day before next cycle)


class AIRACCalculator:
    """
    Calculator for AIRAC (Aeronautical Information Regulation And Control) cycles.
    
    AIRAC cycles are used in aviation for the scheduled publication of 
    aeronautical information. Each cycle is exactly 28 days long.
    
    Reference: ICAO Doc 8126, Section 2.6.2
    """
    
    # Reference date: A known AIRAC effective date
    # Using 2020-01-02 as it's a well-documented AIRAC start date
    # Source: https://www.icao.int/airnavigation/information-management/Pages/AIRAC.aspx
    EPOCH = date(2020, 1, 2)
    
    # Each AIRAC cycle is exactly 28 days
    CYCLE_DAYS = 28
    
    @classmethod
    def from_date(cls, query_date: date | None = None) -> AIRACCycle:
        """
        Get the AIRAC cycle that is effective on the given date.
        
        Args:
            query_date: The date to query. Defaults to today.
            
        Returns:
            AIRACCycle containing all cycle information.
        """
        if query_date is None:
            query_date = date.today()
        
        # Calculate the number of complete cycles since the epoch
        days_since_epoch = (query_date - cls.EPOCH).days
        cycles_since_epoch = days_since_epoch // cls.CYCLE_DAYS
        
        # Calculate the effective date of the current cycle
        effective_date = cls.EPOCH + timedelta(days=cycles_since_epoch * cls.CYCLE_DAYS)
        
        # Calculate expiration date (day before next cycle starts)
        expiration_date = effective_date + timedelta(days=cls.CYCLE_DAYS - 1)
        
        # Calculate the ordinal (cycle number within the year)
        year = effective_date.year
        year_start = date(year, 1, 1)
        
        # Find the first cycle that starts in this year
        days_from_epoch_to_year_start = (year_start - cls.EPOCH).days
        first_cycle_of_year_offset = days_from_epoch_to_year_start % cls.CYCLE_DAYS
        
        if first_cycle_of_year_offset > 0:
            first_cycle_start = year_start + timedelta(days=cls.CYCLE_DAYS - first_cycle_of_year_offset)
        else:
            first_cycle_start = year_start
        
        # If the effective date is before the first cycle of the year,
        # this cycle belongs to the previous year
        if effective_date < first_cycle_start:
            year = effective_date.year - 1
            year_start = date(year, 1, 1)
            days_from_epoch_to_year_start = (year_start - cls.EPOCH).days
            first_cycle_of_year_offset = days_from_epoch_to_year_start % cls.CYCLE_DAYS
            if first_cycle_of_year_offset > 0:
                first_cycle_start = year_start + timedelta(days=cls.CYCLE_DAYS - first_cycle_of_year_offset)
            else:
                first_cycle_start = year_start
        
        # Calculate ordinal (1-based)
        ordinal = ((effective_date - first_cycle_start).days // cls.CYCLE_DAYS) + 1
        
        # Format identifier as YYCC
        identifier = f"{year % 100:02d}{ordinal:02d}"
        
        return AIRACCycle(
            identifier=identifier,
            year=year,
            ordinal=ordinal,
            effective_date=effective_date,
            expiration_date=expiration_date
        )
    
    @classmethod
    def from_identifier(cls, identifier: str) -> AIRACCycle:
        """
        Get an AIRAC cycle from its identifier (YYCC format).
        
        Args:
            identifier: AIRAC identifier in YYCC format (e.g., "2513").
                       Years 64-99 are interpreted as 1964-1999.
                       Years 00-63 are interpreted as 2000-2063.
                       
        Returns:
            AIRACCycle containing all cycle information.
            
        Raises:
            ValueError: If the identifier is invalid.
        """
        if len(identifier) != 4 or not identifier.isdigit():
            raise ValueError(f"Invalid AIRAC identifier: {identifier}")
        
        year_part = int(identifier[:2])
        ordinal = int(identifier[2:])
        
        # Determine full year
        if year_part >= 64:
            year = 1900 + year_part
        else:
            year = 2000 + year_part
        
        if ordinal < 1 or ordinal > 14:
            raise ValueError(f"Invalid ordinal in AIRAC identifier: {identifier}")
        
        # Find the last cycle of the previous year
        prev_year_end = date(year - 1, 12, 31)
        last_cycle_prev_year = cls.from_date(prev_year_end)
        
        # Calculate the effective date by adding ordinal cycles
        cycles_to_add = ordinal
        target_effective = last_cycle_prev_year.effective_date + timedelta(days=cycles_to_add * cls.CYCLE_DAYS)
        
        # Verify the calculated cycle matches the expected year
        result = cls.from_date(target_effective)
        if result.year != year or result.ordinal != ordinal:
            raise ValueError(f"Invalid AIRAC identifier: {identifier}")
        
        return result
    
    @classmethod
    def current(cls) -> AIRACCycle:
        """Get the current AIRAC cycle."""
        return cls.from_date(date.today())
    
    @classmethod
    def next(cls, cycle: AIRACCycle | None = None) -> AIRACCycle:
        """Get the next AIRAC cycle after the given cycle (or current if not specified)."""
        if cycle is None:
            cycle = cls.current()
        next_date = cycle.effective_date + timedelta(days=cls.CYCLE_DAYS)
        return cls.from_date(next_date)
    
    @classmethod
    def previous(cls, cycle: AIRACCycle | None = None) -> AIRACCycle:
        """Get the previous AIRAC cycle before the given cycle (or current if not specified)."""
        if cycle is None:
            cycle = cls.current()
        prev_date = cycle.effective_date - timedelta(days=1)
        return cls.from_date(prev_date)


# Example usage and testing
if __name__ == "__main__":
    calc = AIRACCalculator()
    
    # Get current cycle
    current = calc.current()
    print(f"Current AIRAC Cycle: {current.identifier}")
    print(f"  Year: {current.year}, Ordinal: {current.ordinal}")
    print(f"  Effective: {current.effective_date}")
    print(f"  Expires: {current.expiration_date}")
    
    # Get next cycle
    next_cycle = calc.next()
    print(f"\nNext AIRAC Cycle: {next_cycle.identifier}")
    print(f"  Effective: {next_cycle.effective_date}")
    
    # Test with known dates
    test_dates = [
        date(2020, 1, 2),   # Should be 2001
        date(2020, 1, 30),  # Should be 2002
        date(2020, 12, 31), # Should be 2014 (2020 has 14 cycles)
        date(2025, 11, 25), # Current date from context
    ]
    
    print("\nTest cases:")
    for test_date in test_dates:
        cycle = calc.from_date(test_date)
        print(f"  {test_date} -> {cycle.identifier} (effective: {cycle.effective_date})")
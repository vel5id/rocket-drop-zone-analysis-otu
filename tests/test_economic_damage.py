"""
Unit tests for economic damage assessment module.

Tests for:
1. EconomicDamageCalculator class (Task 5.1 implementation)
2. Legacy functions (backward compatibility)
3. Currency conversion (KZT to USD)
4. All damage components: vegetation, soil, fire, contamination, mechanical

Test data based on IMPLEMENTATION_ROADMAP.md specifications.
"""
import numpy as np
import pytest
from otu.economic_damage import (
    EconomicDamageCalculator,
    EconomicConfig,
    compute_fire_damage_cost,
    compute_soil_damage_cost,
    compute_vegetation_damage_cost,
    compute_total_restoration_cost,
    compute_impact_zone_cost,
    calculate_comprehensive_damage,
)


class TestEconomicDamageCalculator:
    """Tests for EconomicDamageCalculator class (Task 5.1)."""
    
    def setup_method(self):
        """Initialize calculator for each test."""
        self.calculator = EconomicDamageCalculator(usd_to_kzt=450.0)
    
    def test_initialization(self):
        """Test calculator initialization with unit costs."""
        assert self.calculator.usd_to_kzt == 450.0
        assert 'vegetation_loss' in self.calculator.costs_kzt
        assert 'contamination' in self.calculator.costs_kzt
        assert 'mechanical_damage' in self.calculator.costs_kzt
        
        # Check unit cost values from roadmap (lines 659-665)
        assert self.calculator.costs_kzt['vegetation_loss'] == 50000
        assert self.calculator.costs_kzt['soil_degradation'] == 30000
        assert self.calculator.costs_kzt['fire_risk'] == 20000
        assert self.calculator.costs_kzt['contamination'] == 40000
        assert self.calculator.costs_kzt['mechanical_damage'] == 25000
    
    def test_calculate_vegetation_cost(self):
        """Test vegetation cost calculation."""
        # Test data: single cell with q_ndvi = 0.3 (70% damage)
        otu_results = np.array([[0.3, 0.5, 0.5, 0.5, 0.5, 0.5]])  # [q_ndvi, q_si, q_bi, q_relief, q_otu, q_fire]
        area_ha = 100.0  # 1 km² = 100 ha
        
        cost = self.calculator._calculate_vegetation_cost(otu_results, area_ha)
        
        # Expected: 50000 * (1 - 0.3) * 100 = 50000 * 0.7 * 100 = 3,500,000 KZT
        expected = 50000 * 0.7 * 100
        assert pytest.approx(cost, rel=0.01) == expected
    
    def test_calculate_soil_cost(self):
        """Test soil degradation cost calculation."""
        # Test data: single cell with q_si=0.4, q_bi=0.6 (average 0.5, 50% damage)
        otu_results = np.array([[0.5, 0.4, 0.6, 0.5, 0.5, 0.5]])
        area_ha = 100.0
        
        cost = self.calculator._calculate_soil_cost(otu_results, area_ha)
        
        # Expected: 30000 * (1 - 0.5) * 100 = 30000 * 0.5 * 100 = 1,500,000 KZT
        expected = 30000 * 0.5 * 100
        assert pytest.approx(cost, rel=0.01) == expected
    
    def test_calculate_fire_cost(self):
        """Test fire risk cost calculation."""
        # Test data: single cell with q_fire=0.8 (high fire risk)
        otu_results = np.array([[0.5, 0.5, 0.5, 0.5, 0.5, 0.8]])
        area_ha = 100.0
        
        cost = self.calculator._calculate_fire_cost(otu_results, area_ha)
        
        # Expected: 20000 * 0.8 * 100 = 1,600,000 KZT
        expected = 20000 * 0.8 * 100
        assert pytest.approx(cost, rel=0.01) == expected
    
    def test_calculate_contamination_cost(self):
        """Test contamination cleanup cost calculation."""
        # Test data: poor soil (q_bi=0.2) and poor vegetation (q_ndvi=0.3)
        otu_results = np.array([[0.3, 0.5, 0.2, 0.5, 0.5, 0.5]])
        area_ha = 100.0
        
        cost = self.calculator._calculate_contamination_cost(otu_results, area_ha)
        
        # contamination_factor = (1 - 0.2) * (1 - 0.3) = 0.8 * 0.7 = 0.56
        # Expected: 40000 * 0.56 * 100 = 2,240,000 KZT
        expected = 40000 * 0.56 * 100
        assert pytest.approx(cost, rel=0.01) == expected
    
    def test_calculate_mechanical_cost(self):
        """Test mechanical damage cost calculation."""
        # Test data: weak soil (q_si=0.3) and complex relief (q_relief=0.2)
        otu_results = np.array([[0.5, 0.3, 0.5, 0.2, 0.5, 0.5]])
        area_ha = 100.0
        
        cost = self.calculator._calculate_mechanical_cost(otu_results, area_ha)
        
        # mechanical_factor = (1 - 0.3) * (1 - 0.2) = 0.7 * 0.8 = 0.56
        # Expected: 25000 * 0.56 * 100 = 1,400,000 KZT
        expected = 25000 * 0.56 * 100
        assert pytest.approx(cost, rel=0.01) == expected
    
    def test_calculate_total_damage_single_cell(self):
        """Test comprehensive damage calculation for single cell."""
        # Representative OTU cell (OTU_245 from roadmap lines 728-735)
        otu_results = np.array([[0.45, 0.35, 0.28, 0.82, 0.31, 0.52]])
        cell_size_km = 1.0
        
        result = self.calculator.calculate_total_damage(otu_results, cell_size_km)
        
        # Verify structure
        assert 'total_area_ha' in result
        assert 'grand_total_kzt' in result
        assert 'grand_total_usd' in result
        assert 'percentages' in result
        
        # Verify area calculation
        assert result['total_area_ha'] == 100.0  # 1 km² = 100 ha
        assert result['num_cells'] == 1
        assert result['cell_area_ha'] == 100.0
        
        # Verify all cost components present
        assert 'vegetation_cost_kzt' in result
        assert 'soil_cost_kzt' in result
        assert 'fire_cost_kzt' in result
        assert 'contamination_cost_kzt' in result
        assert 'mechanical_cost_kzt' in result
        
        # Verify USD conversion
        expected_usd = result['grand_total_kzt'] / 450.0
        assert pytest.approx(result['grand_total_usd'], rel=0.01) == expected_usd
        
        # Verify percentages sum to ~100%
        percentages = result['percentages']
        total_pct = sum(percentages.values())
        assert pytest.approx(total_pct, rel=0.01) == 100.0
    
    def test_calculate_total_damage_multiple_cells(self):
        """Test damage calculation for multiple OTU cells."""
        # Create 3 cells with different characteristics
        otu_results = np.array([
            [0.8, 0.7, 0.6, 0.9, 0.75, 0.2],  # Good conditions
            [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],  # Average conditions
            [0.2, 0.3, 0.4, 0.1, 0.25, 0.8],  # Poor conditions
        ])
        cell_size_km = 1.0
        
        result = self.calculator.calculate_total_damage(otu_results, cell_size_km)
        
        # Verify totals
        assert result['num_cells'] == 3
        assert result['total_area_ha'] == 300.0  # 3 * 100 ha
        
        # Costs should be positive
        assert result['grand_total_kzt'] > 0
        assert result['grand_total_usd'] > 0
        
        # Poor condition cell should have higher costs
        # (verification through component calculations)
    
    def test_empty_results(self):
        """Test calculator with empty OTU results."""
        otu_results = np.array([]).reshape(0, 6)
        
        result = self.calculator.calculate_total_damage(otu_results)
        
        assert result['num_cells'] == 0
        assert result['total_area_ha'] == 0.0
        assert result['grand_total_kzt'] == 0.0
        assert result['grand_total_usd'] == 0.0
    
    def test_custom_exchange_rate(self):
        """Test calculator with custom exchange rate."""
        calculator = EconomicDamageCalculator(usd_to_kzt=500.0)  # 1 USD = 500 KZT
        otu_results = np.array([[0.5, 0.5, 0.5, 0.5, 0.5, 0.5]])
        
        result = calculator.calculate_total_damage(otu_results)
        
        # Verify custom exchange rate
        assert calculator.usd_to_kzt == 500.0
        assert result['exchange_rate'] == 500.0
        assert result['grand_total_usd'] == result['grand_total_kzt'] / 500.0


class TestLegacyFunctions:
    """Tests for legacy functions (backward compatibility)."""
    
    def test_compute_fire_damage_cost(self):
        """Test fire damage cost calculation."""
        config = EconomicConfig(fire_base_cost=5000.0)
        
        # Single value
        cost = compute_fire_damage_cost(0.7, area_ha=100.0, config=config)
        assert pytest.approx(cost, rel=0.01) == 5000.0 * 0.7 * 100.0
        
        # Array input
        q_fire = np.array([0.3, 0.6, 0.9])
        costs = compute_fire_damage_cost(q_fire, area_ha=50.0, config=config)
        assert len(costs) == 3
        assert pytest.approx(costs[2], rel=0.01) == 5000.0 * 0.9 * 50.0
    
    def test_compute_soil_damage_cost(self):
        """Test soil damage cost calculation."""
        config = EconomicConfig(
            soil_strength_base=3000.0,
            soil_quality_base=4000.0
        )
        
        strength_cost, quality_cost = compute_soil_damage_cost(
            q_si=0.4, q_bi=0.6, area_ha=100.0, config=config
        )
        
        # strength_damage = 1 - 0.4 = 0.6
        # quality_damage = 1 - 0.6 = 0.4
        expected_strength = 3000.0 * 0.6 * 100.0
        expected_quality = 4000.0 * 0.4 * 100.0
        
        assert pytest.approx(strength_cost, rel=0.01) == expected_strength
        assert pytest.approx(quality_cost, rel=0.01) == expected_quality
    
    def test_compute_vegetation_damage_cost(self):
        """Test vegetation damage cost calculation."""
        config = EconomicConfig(
            vegetation_base=8000.0,
            vegetation_recovery_factor=2.0
        )
        
        cost = compute_vegetation_damage_cost(
            q_vi=0.3, area_ha=100.0, config=config
        )
        
        # veg_damage = 1 - 0.3 = 0.7
        # Expected: 8000 * 0.7 * 2.0 * 100 = 1,120,000
        expected = 8000.0 * 0.7 * 2.0 * 100.0
        assert pytest.approx(cost, rel=0.01) == expected
    
    def test_compute_total_restoration_cost(self):
        """Test total restoration cost calculation."""
        config = EconomicConfig()
        
        result = compute_total_restoration_cost(
            q_vi=0.4, q_si=0.5, q_bi=0.6, q_fire=0.3,
            area_ha=100.0, config=config
        )
        
        assert 'fire_cost' in result
        assert 'soil_strength_cost' in result
        assert 'soil_quality_cost' in result
        assert 'vegetation_cost' in result
        assert 'total_cost' in result
        
        # Verify total is sum of components
        total = (result['fire_cost'] + result['soil_strength_cost'] + 
                 result['soil_quality_cost'] + result['vegetation_cost'])
        assert pytest.approx(result['total_cost'], rel=0.01) == total
    
    def test_compute_impact_zone_cost(self):
        """Test impact zone cost calculation."""
        # Create sample OTU results
        otu_results = np.array([
            [0.6, 0.7, 0.8, 0.5, 0.65, 0.2],  # Cell 1
            [0.4, 0.5, 0.6, 0.5, 0.5, 0.4],   # Cell 2
            [0.2, 0.3, 0.4, 0.5, 0.3, 0.6],   # Cell 3
        ])
        
        result = compute_impact_zone_cost(otu_results, cell_size_km=1.0)
        
        assert 'num_cells' in result
        assert 'total_area_ha' in result
        assert 'grand_total' in result
        assert 'cost_per_cell_mean' in result
        
        assert result['num_cells'] == 3
        assert result['total_area_ha'] == 300.0  # 3 * 100 ha
        assert result['grand_total'] > 0
        
        # Verify statistics
        assert result['cost_per_cell_min'] <= result['cost_per_cell_mean']
        assert result['cost_per_cell_mean'] <= result['cost_per_cell_max']


class TestConvenienceFunction:
    """Tests for calculate_comprehensive_damage convenience function."""
    
    def test_convenience_function(self):
        """Test the convenience function wrapper."""
        otu_results = np.array([[0.5, 0.5, 0.5, 0.5, 0.5, 0.5]])
        
        result = calculate_comprehensive_damage(
            otu_results, 
            cell_size_km=1.0,
            usd_to_kzt=450.0
        )
        
        # Should have same structure as calculator result
        assert 'grand_total_kzt' in result
        assert 'grand_total_usd' in result
        assert 'percentages' in result
        
        # Verify exchange rate
        assert result['exchange_rate'] == 450.0


class TestIntegration:
    """Integration tests for economic damage module."""
    
    def test_backward_compatibility(self):
        """Verify that legacy code still works with new implementation."""
        # Sample data from run_otu_pipeline.py
        otu_results = np.array([
            [0.65, 0.72, 0.58, 0.81, 0.69, 0.15],
            [0.42, 0.38, 0.47, 0.63, 0.42, 0.28],
            [0.23, 0.19, 0.31, 0.42, 0.25, 0.52],
        ])
        
        # Test legacy function
        legacy_result = compute_impact_zone_cost(otu_results, cell_size_km=1.0)
        assert legacy_result['num_cells'] == 3
        assert legacy_result['grand_total'] > 0
        
        # Test new calculator
        calculator = EconomicDamageCalculator()
        new_result = calculator.calculate_total_damage(otu_results, cell_size_km=1.0)
        assert new_result['num_cells'] == 3
        assert new_result['grand_total_kzt'] > 0
        
        # Both should produce valid results (values may differ due to different formulas)
    
    def test_currency_conversion_accuracy(self):
        """Test accuracy of KZT to USD conversion."""
        calculator = EconomicDamageCalculator(usd_to_kzt=450.0)
        
        # Test with known values
        test_cases = [
            (450000, 1000),   # 450,000 KZT = 1,000 USD
            (225000, 500),    # 225,000 KZT = 500 USD
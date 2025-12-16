"""
Statistical analytics for trading data
Includes: z-score, rolling correlation, basic statistics
"""
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.stattools import adfuller
from sklearn.linear_model import LinearRegression

class TradingAnalytics:
    """
    Core analytics for pairs trading and statistical arbitrage
    """
    
    def __init__(self):
        pass
    
    def calculate_zscore(self, series, window=20):
        """
        Calculate rolling z-score
        
        Args:
            series (pd.Series): Price series
            window (int): Rolling window size
        
        Returns:
            pd.Series: Z-score values
        """
        try:
            rolling_mean = series.rolling(window=window).mean()
            rolling_std = series.rolling(window=window).std()
            zscore = (series - rolling_mean) / rolling_std
            return zscore
        except Exception as e:
            print(f"❌ Error calculating z-score: {e}")
            return pd.Series()
    
    def calculate_spread(self, series1, series2, hedge_ratio=1.0):
        """
        Calculate spread between two price series
        
        Args:
            series1 (pd.Series): First price series
            series2 (pd.Series): Second price series
            hedge_ratio (float): Hedge ratio (from regression)
        
        Returns:
            pd.Series: Spread values
        """
        try:
            spread = series1 - (hedge_ratio * series2)
            return spread
        except Exception as e:
            print(f"❌ Error calculating spread: {e}")
            return pd.Series()
    
    def calculate_hedge_ratio(self, series1, series2):
        """
        Calculate hedge ratio using OLS regression
        
        Args:
            series1 (pd.Series): Dependent variable (Y)
            series2 (pd.Series): Independent variable (X)
        
        Returns:
            dict: {'hedge_ratio': float, 'intercept': float, 'r_squared': float}
        """
        try:
            # Remove NaN values
            df = pd.DataFrame({'y': series1, 'x': series2}).dropna()
            
            if len(df) < 2:
                return {'hedge_ratio': 1.0, 'intercept': 0.0, 'r_squared': 0.0}
            
            X = df['x'].values.reshape(-1, 1)
            y = df['y'].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            hedge_ratio = model.coef_[0]
            intercept = model.intercept_
            r_squared = model.score(X, y)
            
            return {
                'hedge_ratio': hedge_ratio,
                'intercept': intercept,
                'r_squared': r_squared
            }
            
        except Exception as e:
            print(f"❌ Error calculating hedge ratio: {e}")
            return {'hedge_ratio': 1.0, 'intercept': 0.0, 'r_squared': 0.0}
    
    def adf_test(self, series):
        """
        Augmented Dickey-Fuller test for stationarity
        
        Args:
            series (pd.Series): Time series to test
        
        Returns:
            dict: Test results including p-value and test statistic
        """
        try:
            series_clean = series.dropna()
            
            if len(series_clean) < 10:
                return {
                    'statistic': None,
                    'pvalue': None,
                    'is_stationary': False,
                    'error': 'Insufficient data'
                }
            
            result = adfuller(series_clean, autolag='AIC')
            
            return {
                'statistic': result[0],
                'pvalue': result[1],
                'critical_values': result[4],
                'is_stationary': result[1] < 0.05  # p-value < 0.05 means stationary
            }
            
        except Exception as e:
            print(f"❌ Error in ADF test: {e}")
            return {
                'statistic': None,
                'pvalue': None,
                'is_stationary': False,
                'error': str(e)
            }
    
    def rolling_correlation(self, series1, series2, window=20):
        """
        Calculate rolling correlation between two series
        
        Args:
            series1 (pd.Series): First series
            series2 (pd.Series): Second series
            window (int): Rolling window
        
        Returns:
            pd.Series: Rolling correlation values
        """
        try:
            df = pd.DataFrame({'s1': series1, 's2': series2})
            corr = df['s1'].rolling(window=window).corr(df['s2'])
            return corr
        except Exception as e:
            print(f"❌ Error calculating rolling correlation: {e}")
            return pd.Series()
    
    def calculate_volatility(self, returns, window=20):
        """
        Calculate rolling volatility
        
        Args:
            returns (pd.Series): Return series
            window (int): Rolling window
        
        Returns:
            pd.Series: Rolling volatility
        """
        try:
            volatility = returns.rolling(window=window).std() * np.sqrt(window)
            return volatility
        except Exception as e:
            print(f"❌ Error calculating volatility: {e}")
            return pd.Series()
    
    def calculate_returns(self, prices):
        """
        Calculate simple returns
        
        Args:
            prices (pd.Series): Price series
        
        Returns:
            pd.Series: Returns
        """
        try:
            returns = prices.pct_change()
            return returns
        except Exception as e:
            print(f"❌ Error calculating returns: {e}")
            return pd.Series()
    
    def basic_statistics(self, series):
        """
        Calculate basic statistics
        
        Args:
            series (pd.Series): Data series
        
        Returns:
            dict: Statistics including mean, std, min, max, etc.
        """
        try:
            return {
                'mean': series.mean(),
                'median': series.median(),
                'std': series.std(),
                'min': series.min(),
                'max': series.max(),
                'skew': series.skew(),
                'kurtosis': series.kurtosis(),
                'count': len(series)
            }
        except Exception as e:
            print(f"❌ Error calculating statistics: {e}")
            return {}


if __name__ == "__main__":
    """Test analytics functions"""
    print("=" * 60)
    print("Testing Analytics Module")
    print("=" * 60)
    
    # Create sample data
    np.random.seed(42)
    n = 100
    
    # Two correlated price series
    series1 = pd.Series(100 + np.cumsum(np.random.randn(n) * 0.5))
    series2 = pd.Series(50 + np.cumsum(np.random.randn(n) * 0.3))
    
    analytics = TradingAnalytics()
    
    # Test hedge ratio
    print("\n📊 Testing Hedge Ratio (OLS Regression):")
    hedge = analytics.calculate_hedge_ratio(series1, series2)
    print(f"   Hedge Ratio: {hedge['hedge_ratio']:.4f}")
    print(f"   R-squared: {hedge['r_squared']:.4f}")
    
    # Test spread and z-score
    print("\n📊 Testing Spread & Z-Score:")
    spread = analytics.calculate_spread(series1, series2, hedge['hedge_ratio'])
    zscore = analytics.calculate_zscore(spread, window=20)
    print(f"   Current Spread: {spread.iloc[-1]:.4f}")
    print(f"   Current Z-Score: {zscore.iloc[-1]:.4f}")
    
    # Test ADF
    print("\n📊 Testing ADF Stationarity Test:")
    adf = analytics.adf_test(spread)
    print(f"   P-value: {adf['pvalue']:.4f}")
    print(f"   Is Stationary: {adf['is_stationary']}")
    
    # Test correlation
    print("\n📊 Testing Rolling Correlation:")
    corr = analytics.rolling_correlation(series1, series2, window=20)
    print(f"   Current Correlation: {corr.iloc[-1]:.4f}")
    
    # Test basic stats
    print("\n📊 Testing Basic Statistics:")
    stats = analytics.basic_statistics(series1)
    print(f"   Mean: {stats['mean']:.2f}")
    print(f"   Std: {stats['std']:.2f}")
    
    print("\n✅ Analytics module test complete!")
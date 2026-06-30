pub mod individual;
pub mod accumulated;
pub mod scaled_parallel;

pub use individual::IndividualResult;
pub use accumulated::{AccumulatedResult, RssSample};
pub use scaled_parallel::{ScaledParallelResult, ScaleCurvePoint};

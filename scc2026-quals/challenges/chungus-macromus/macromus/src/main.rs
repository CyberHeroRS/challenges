use paste::paste;

pub fn validate<T: Valid>() {}

macro_rules! __scc_ty {
    ($base:ty; 0) => {
        <$base as SCC>::N0
    };
    ($base:ty; 1) => {
        <$base as SCC>::N1
    };
    ($base:ty; 2) => {
        <$base as SCC>::N2
    };
    ($base:ty; 3) => {
        <$base as SCC>::N3
    };
    ($base:ty; 4) => {
        <$base as SCC>::N4
    };
    ($base:ty; 5) => {
        <$base as SCC>::N5
    };
    ($base:ty; 6) => {
        <$base as SCC>::N6
    };
    ($base:ty; 7) => {
        <$base as SCC>::N7
    };
    ($base:ty; 8) => {
        <$base as SCC>::N8
    };
    ($base:ty; 9) => {
        <$base as SCC>::N9
    };
    ($base:ty; $x:ident) => {
        <$base as SCC>::$x
    };
}

macro_rules! __scc_chain {
    ($base:ty; $a:tt $b:tt $c:tt $d:tt) => {
        __scc_ty!(
            __scc_ty!(
                __scc_ty!(
                    __scc_ty!($base; $a);
                    $b
                );
                $c
            );
            $d
        )
    };
}

macro_rules! __scc_chunk {
    ($idx:literal; $a:tt $b:tt $c:tt $d:tt) => {
        paste! {
            validate::<__scc_chain!([<Check $idx _0>]; $a $b $c $d)>();
            validate::<__scc_chain!([<Check $idx _1>]; $a $b $c $d)>();
            validate::<__scc_chain!([<Check $idx _2>]; $a $b $c $d)>();
            validate::<__scc_chain!([<Check $idx _3>]; $a $b $c $d)>();
        }
    };
}

macro_rules! SCC {
    (
        $a0:tt $a1:tt $a2:tt $a3:tt
        $b0:tt $b1:tt $b2:tt $b3:tt
        $c0:tt $c1:tt $c2:tt $c3:tt
        $d0:tt $d1:tt $d2:tt $d3:tt
        $e0:tt $e1:tt $e2:tt $e3:tt
    ) => {
        __scc_chunk!(0; $a0 $a1 $a2 $a3);
        __scc_chunk!(1; $b0 $b1 $b2 $b3);
        __scc_chunk!(2; $c0 $c1 $c2 $c3);
        __scc_chunk!(3; $d0 $d1 $d2 $d3);
        __scc_chunk!(4; $e0 $e1 $e2 $e3);
    };

    ($($anything:tt)*) => {
        compile_error!("SCC! requires exactly 20 chars");
    };
}

fn main() {
    SCC! {F A K E F L A G F A K E F L A G F A K E};
}

pub trait SCC {
    type A;
    type B;
    type C;
    type D;
    type E;
    type F;
    type G;
    type H;
    type I;
    type J;
    type K;
    type L;
    type M;
    type N;
    type O;
    type P;
    type Q;
    type R;
    type S;
    type T;
    type U;
    type V;
    type W;
    type X;
    type Y;
    type Z;

    type N0;
    type N1;
    type N2;
    type N3;
    type N4;
    type N5;
    type N6;
    type N7;
    type N8;
    type N9;
}

pub trait Valid {}
pub struct True;
pub struct False;
impl Valid for True {}

impl<
        TA,
        TB,
        TC,
        TD,
        TE,
        TF,
        TG,
        TH,
        TI,
        TJ,
        TK,
        TL,
        TM,
        TN,
        TO,
        TP,
        TQ,
        TR,
        TS,
        TT,
        TU,
        TV,
        TW,
        TX,
        TY,
        TZ,
        TN0,
        TN1,
        TN2,
        TN3,
        TN4,
        TN5,
        TN6,
        TN7,
        TN8,
        TN9,
    > SCC
    for (
        TA,
        TB,
        TC,
        TD,
        TE,
        TF,
        TG,
        TH,
        TI,
        TJ,
        TK,
        TL,
        TM,
        TN,
        TO,
        TP,
        TQ,
        TR,
        TS,
        TT,
        TU,
        TV,
        TW,
        TX,
        TY,
        TZ,
        TN0,
        TN1,
        TN2,
        TN3,
        TN4,
        TN5,
        TN6,
        TN7,
        TN8,
        TN9,
    )
{
    type A = TA;
    type B = TB;
    type C = TC;
    type D = TD;
    type E = TE;
    type F = TF;
    type G = TG;
    type H = TH;
    type I = TI;
    type J = TJ;
    type K = TK;
    type L = TL;
    type M = TM;
    type N = TN;
    type O = TO;
    type P = TP;
    type Q = TQ;
    type R = TR;
    type S = TS;
    type T = TT;
    type U = TU;
    type V = TV;
    type W = TW;
    type X = TX;
    type Y = TY;
    type Z = TZ;

    type N0 = TN0;
    type N1 = TN1;
    type N2 = TN2;
    type N3 = TN3;
    type N4 = TN4;
    type N5 = TN5;
    type N6 = TN6;
    type N7 = TN7;
    type N8 = TN8;
    type N9 = TN9;
}

include! {concat!(env!("CARGO_MANIFEST_DIR"), "/macromus.rs")}

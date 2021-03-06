import mock
import numpy
import six
import threading
import unittest

import cupy
from cupy import testing


def fusion_default_array_equal():
    def deco(func):
        def wrapper(self_x, name, xp, **dtypes):
            @cupy.fuse()
            def f(*args):
                return getattr(xp, name)(*args)
            args = func(self_x, name, xp, **dtypes)
            return f(*args)
        return wrapper
    return deco


@testing.gpu
class TestFusionElementwise(unittest.TestCase):

    @testing.for_int_dtypes()
    @testing.numpy_cupy_array_equal()
    @fusion_default_array_equal()
    def check_unary_int(self, name, xp, dtype):
        a = xp.array([-3, -2, -1, 0, 1, 2, 3], dtype=dtype)
        return (a,)

    @testing.for_int_dtypes()
    @testing.numpy_cupy_array_equal()
    @fusion_default_array_equal()
    def check_binary_int(self, name, xp, dtype):
        a = xp.array([-3, -2, -1, 0, 1, 2, 3], dtype=dtype)
        b = xp.array([0, 1, 2, 3, 4, 5, 6], dtype=dtype)
        return a, b

    def test_bitwise_and(self):
        self.check_binary_int('bitwise_and')

    def test_bitwise_or(self):
        self.check_binary_int('bitwise_or')

    def test_bitwise_xor(self):
        self.check_binary_int('bitwise_xor')

    def test_invert(self):
        self.check_unary_int('invert')

    def test_left_shift(self):
        self.check_binary_int('left_shift')

    def test_right_shift(self):
        self.check_binary_int('right_shift')


@testing.gpu
class TestFusionComparison(unittest.TestCase):

    @testing.for_all_dtypes_combination(
        no_complex=True, names=['dtype1', 'dtype2'])
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_binary(self, name, xp, dtype1, dtype2):
        a = testing.shaped_arange((2, 3), xp, dtype1)
        b = testing.shaped_reverse_arange((2, 3), xp, dtype2)
        return a, b

    def test_greater(self):
        self.check_binary('greater')

    def test_greater_equal(self):
        self.check_binary('greater_equal')

    def test_less(self):
        self.check_binary('less')

    def test_less_equal(self):
        self.check_binary('less_equal')

    def test_not_equal(self):
        self.check_binary('not_equal')

    def test_equal(self):
        self.check_binary('equal')


@testing.gpu
class TestFusionContent(unittest.TestCase):

    @testing.for_float_dtypes()
    @testing.numpy_cupy_array_equal()
    @fusion_default_array_equal()
    def check_unary_inf(self, name, xp, dtype):
        a = xp.array([-3, dtype('inf'), -1, -dtype('inf'), 0, 1, 2],
                     dtype=dtype)
        return (a,)

    @testing.for_float_dtypes()
    @testing.numpy_cupy_array_equal()
    @fusion_default_array_equal()
    def check_unary_nan(self, name, xp, dtype):
        a = xp.array(
            [-3, numpy.NAN, -1, numpy.NAN, 0, numpy.NAN, dtype('inf')],
            dtype=dtype)
        return (a,)

    def test_isfinite(self):
        self.check_unary_inf('isfinite')

    def test_isinf(self):
        self.check_unary_inf('isinf')

    def test_isnan(self):
        self.check_unary_nan('isnan')


@testing.gpu
class TestFusionOps(unittest.TestCase):

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_unary(self, name, xp, dtype):
        a = testing.shaped_arange((2, 3), xp, dtype)
        return (a,)

    @testing.for_all_dtypes_combination(
        no_complex=True, names=['dtype1', 'dtype2'])
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_binary(self, name, xp, dtype1, dtype2):
        a = testing.shaped_arange((2, 3), xp, dtype1)
        b = testing.shaped_reverse_arange((2, 3), xp, dtype2)
        return a, b

    def test_logical_and(self):
        self.check_binary('logical_and')

    def test_logical_or(self):
        self.check_binary('logical_or')

    def test_logical_xor(self):
        self.check_binary('logical_xor')

    def test_logical_not(self):
        self.check_unary('logical_not')


@testing.gpu
class TestFusionTrigonometric(unittest.TestCase):

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_unary(self, name, xp, dtype):
        a = testing.shaped_arange((2, 3), xp, dtype)
        return (a,)

    @testing.for_all_dtypes_combination(
        no_complex=True, names=['dtype1', 'dtype2'])
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_binary(self, name, xp, dtype1, dtype2):
        a = testing.shaped_arange((2, 3), xp, dtype1)
        b = testing.shaped_reverse_arange((2, 3), xp, dtype2)
        return a, b

    @testing.for_dtypes(['e', 'f', 'd'])
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_unary_unit(self, name, xp, dtype):
        a = xp.array([0.2, 0.4, 0.6, 0.8], dtype=dtype)
        return (a,)

    def test_sin(self):
        self.check_unary('sin')

    def test_cos(self):
        self.check_unary('cos')

    def test_tan(self):
        self.check_unary('tan')

    def test_arcsin(self):
        self.check_unary_unit('arcsin')

    def test_arccos(self):
        self.check_unary_unit('arccos')

    def test_arctan(self):
        self.check_unary('arctan')

    def test_arctan2(self):
        self.check_binary('arctan2')

    def test_hypot(self):
        self.check_binary('hypot')

    def test_deg2rad(self):
        self.check_unary('deg2rad')

    def test_rad2deg(self):
        self.check_unary('rad2deg')


@testing.gpu
class TestFusionHyperbolic(unittest.TestCase):

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_unary(self, name, xp, dtype):
        a = testing.shaped_arange((2, 3), xp, dtype)
        return (a,)

    @testing.for_dtypes(['e', 'f', 'd'])
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_unary_unit1(self, name, xp, dtype):
        a = xp.array([1, 2, 3], dtype=dtype)
        return (a,)

    @testing.for_dtypes(['e', 'f', 'd'])
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_unary_unit2(self, name, xp, dtype):
        a = xp.array([0.2, 0.4, 0.6, 0.8], dtype=dtype)
        return (a,)

    def test_sinh(self):
        self.check_unary('sinh')

    def test_cosh(self):
        self.check_unary('cosh')

    def test_tanh(self):
        self.check_unary('tanh')

    def test_arcsinh(self):
        self.check_unary('arcsinh')

    def test_arccosh(self):
        self.check_unary_unit1('arccosh')

    def test_arctanh(self):
        self.check_unary_unit2('arctanh')


@testing.gpu
class TestFusionRounding(unittest.TestCase):

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_unary(self, name, xp, dtype):
        a = testing.shaped_arange((2, 3), xp, dtype)
        return (a,)

    @testing.for_dtypes(['?', 'b', 'h', 'i', 'q', 'e', 'f', 'd'])
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_unary_negative(self, name, xp, dtype):
        a = xp.array([-3, -2, -1, 1, 2, 3], dtype=dtype)
        return (a,)

    def test_rint(self):
        self.check_unary('rint')

    def test_rint_negative(self):
        self.check_unary_negative('rint')

    def test_floor(self):
        self.check_unary('floor')

    def test_ceil(self):
        self.check_unary('ceil')

    def test_trunc(self):
        self.check_unary('trunc')

    def test_fix(self):
        self.check_unary('fix')


@testing.gpu
class TestFusionExplog(unittest.TestCase):

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_unary(self, name, xp, dtype):
        a = testing.shaped_arange((2, 3), xp, dtype)
        return (a,)

    @testing.for_all_dtypes_combination(
        no_complex=True, names=['dtype1', 'dtype2'])
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_binary(self, name, xp, dtype1, dtype2):
        a = testing.shaped_arange((2, 3), xp, dtype1)
        b = testing.shaped_reverse_arange((2, 3), xp, dtype2)
        return a, b

    def test_exp(self):
        self.check_unary('exp')

    def test_expm1(self):
        self.check_unary('expm1')

    def test_exp2(self):
        self.check_unary('exp2')

    def test_log(self):
        with testing.NumpyError(divide='ignore'):
            self.check_unary('log')

    def test_log10(self):
        with testing.NumpyError(divide='ignore'):
            self.check_unary('log10')

    def test_log2(self):
        with testing.NumpyError(divide='ignore'):
            self.check_unary('log2')

    def test_log1p(self):
        self.check_unary('log1p')

    def test_logaddexp(self):
        self.check_binary('logaddexp')

    def test_logaddexp2(self):
        self.check_binary('logaddexp2')


@testing.gpu
class TestFusionFloating(unittest.TestCase):

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_unary(self, name, xp, dtype):
        a = testing.shaped_arange((2, 3), xp, dtype)
        return (a,)

    @testing.for_all_dtypes_combination(
        no_complex=True, names=['dtype1', 'dtype2'])
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_binary(self, name, xp, dtype1, dtype2):
        a = testing.shaped_arange((2, 3), xp, dtype1)
        b = testing.shaped_reverse_arange((2, 3), xp, dtype2)
        return a, b

    @testing.for_float_dtypes(name='ftype')
    @testing.for_dtypes(['i', 'l'], name='itype')
    @testing.numpy_cupy_allclose()
    def test_ldexp(self, xp, ftype, itype):
        a = xp.array([-3, -2, -1, 0, 1, 2, 3], dtype=ftype)
        b = xp.array([-3, -2, -1, 0, 1, 2, 3], dtype=itype)

        @cupy.fuse()
        def g(x, y):
            return xp.ldexp(x, y)

        return g(a, b)

    def test_signbit(self):
        self.check_unary('signbit')

    def test_copysign(self):
        self.check_binary('copysign')

    @testing.for_float_dtypes()
    def test_frexp(self, dtype):
        numpy_a = numpy.array([-300, -20, -10, -1, 0, 1, 10, 20, 300],
                              dtype=dtype)

        @cupy.fuse()
        def g(x):
            xp = cupy.get_array_module(x)
            return xp.frexp(x)

        numpy_b, numpy_c = g(numpy_a)

        cupy_a = cupy.array(numpy_a)
        cupy_b, cupy_c = g(cupy_a)

        testing.assert_allclose(cupy_b, numpy_b)
        testing.assert_array_equal(cupy_c, numpy_c)

    def test_nextafter(self):
        self.check_binary('nextafter')


@testing.gpu
class TestFusionArithmetic(unittest.TestCase):

    @testing.for_all_dtypes()
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_unary(self, name, xp, dtype):
        a = testing.shaped_arange((2, 3), xp, dtype)
        return (a,)

    @testing.for_all_dtypes_combination(names=['dtype1', 'dtype2'])
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_binary(self, name, xp, dtype1, dtype2):
        a = testing.shaped_arange((2, 3), xp, dtype1)
        b = testing.shaped_reverse_arange((2, 3), xp, dtype2)
        return a, b

    @testing.for_all_dtypes_combination(
        no_bool=True, no_complex=True, names=['dtype1', 'dtype2'])
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_binary_without_complex_bool(self, name, xp, dtype1, dtype2):
        a = testing.shaped_arange((2, 3), xp, dtype1)
        b = testing.shaped_reverse_arange((2, 3), xp, dtype2)
        return a, b

    @testing.for_all_dtypes_combination(
        no_bool=True, names=['dtype1', 'dtype2'])
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_binary_without_bool(self, name, xp, dtype1, dtype2):
        a = testing.shaped_arange((2, 3), xp, dtype1)
        b = testing.shaped_reverse_arange((2, 3), xp, dtype2)
        return a, b

    @testing.for_dtypes(['?', 'b', 'h', 'i', 'q', 'e', 'f', 'd'])
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_unary_negative(self, name, xp, dtype):
        a = xp.array([-3, -2, -1, 1, 2, 3], dtype=dtype)
        return (a,)

    @testing.for_dtypes_combination(
        ['?', 'b', 'h', 'i', 'q', 'e', 'f', 'd'], names=['dtype1', 'dtype2'])
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_binary_negative(self, name, xp, dtype1, dtype2):
        a = xp.array([-3, -2, -1, 1, 2, 3], dtype=dtype1)
        b = xp.array([4, 3, 2, 1, -1, -2], dtype=dtype2)
        return a, b

    @testing.for_dtypes_combination(
        ['e', 'f', 'd'], names=['dtype1', 'dtype2'])
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_binary_negative_float(self, name, xp, dtype1, dtype2):
        a = xp.array([-3, -2, -1, 1, 2, 3], dtype=dtype1)
        b = xp.array([4, 3, 2, 1, -1, -2], dtype=dtype2)
        return a, b

    def test_add(self):
        self.check_binary('add')

    def test_reciprocal(self):
        with testing.NumpyError(divide='ignore', invalid='ignore'):
            self.check_unary('reciprocal')

    def test_multiply(self):
        self.check_binary('multiply')

    def test_divide(self):
        with testing.NumpyError(divide='ignore'):
            self.check_binary_without_bool('divide')

    def test_divide_negative(self):
        with testing.NumpyError(divide='ignore'):
            self.check_binary_negative('divide')

    def test_power_negative(self):
        self.check_binary_negative_float('power')

    def test_subtract(self):
        # TODO(unno): boolean subtract causes DeprecationWarning in numpy>=1.13
        self.check_binary_without_bool('subtract')

    def test_true_divide(self):
        with testing.NumpyError(divide='ignore'):
            self.check_binary_without_bool('true_divide')

    def test_true_divide_negative(self):
        with testing.NumpyError(divide='ignore'):
            self.check_binary_negative('true_divide')

    def test_floor_divide(self):
        with testing.NumpyError(divide='ignore'):
            self.check_binary_without_complex_bool('floor_divide')

    def test_floor_divide_negative(self):
        with testing.NumpyError(divide='ignore'):
            self.check_binary_negative('floor_divide')

    def test_fmod(self):
        with testing.NumpyError(divide='ignore'):
            self.check_binary_without_complex_bool('fmod')

    def test_fmod_negative(self):
        with testing.NumpyError(divide='ignore'):
            self.check_binary_negative('fmod')

    @testing.for_float_dtypes()
    @testing.numpy_cupy_allclose()
    def test_modf(self, xp, dtype):
        a = xp.array([-2.5, -1.5, -0.5, 0, 0.5, 1.5, 2.5], dtype=dtype)

        @cupy.fuse()
        def g(x):
            return xp.modf(x)

        b, c = g(a)
        d = xp.empty((2, 7), dtype=dtype)
        d[0] = b
        d[1] = c
        return d

    def test_remainder(self):
        with testing.NumpyError(divide='ignore'):
            self.check_binary_without_complex_bool('remainder')

    def test_remainder_negative(self):
        with testing.NumpyError(divide='ignore'):
            self.check_binary_negative('remainder')


@testing.gpu
class TestFusionArithmeticLargeTolerance(unittest.TestCase):

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_allclose(atol=1e-5)
    @fusion_default_array_equal()
    def check_binary_no_complex(self, name, xp, dtype):
        a = testing.shaped_arange((2, 3), xp, dtype) + 1
        b = testing.shaped_reverse_arange((2, 3), xp, dtype) + 1
        return a, b

    @testing.for_complex_dtypes()
    @testing.numpy_cupy_allclose(atol=1e-3)
    @fusion_default_array_equal()
    def check_binary_complex(self, name, xp, dtype):
        a = testing.shaped_arange((2, 3), xp, dtype) + 1
        b = testing.shaped_reverse_arange((2, 3), xp, dtype) + 1
        return a, b

    def test_power(self):
        self.check_binary_no_complex('power')
        self.check_binary_complex('power')


class TestFusionUfunc(unittest.TestCase):

    @cupy.fuse()
    def sample_function(x, y, z):
        xp = cupy.get_array_module(x, y, z)
        return xp.square(xp.add(x, y))

    def random_bool(self, seed=0):
        return testing.shaped_random((3, 3),
                                     xp=cupy,
                                     dtype=numpy.bool_,
                                     seed=seed)

    def random_int(self, lower=-1000, higher=1000, seed=0):
        return testing.shaped_random((3, 3),
                                     xp=cupy,
                                     dtype=numpy.int64,
                                     scale=(higher - lower),
                                     seed=seed) + lower

    def random_real(self, lower=-1000, higher=1000, seed=0):
        return testing.shaped_random((3, 3),
                                     xp=cupy,
                                     dtype=numpy.float64,
                                     scale=(higher - lower),
                                     seed=seed) + lower

    def random_imag(self, lower=-1000, higher=1000, seed=0):
        return testing.shaped_random((3, 3),
                                     xp=cupy,
                                     dtype=numpy.complex128,
                                     scale=(higher - lower),
                                     seed=seed) + lower

    def check(self, func, n, gen, args=None):
        if args is None:
            args = ((),) * n
        self._check(func, n, gen, args)

    def _check(self, func, n, gen, args, error_types=None):
        assert n == len(args), (n, args)
        if error_types is None:
            error_types = ()

        f = cupy.fuse(func)

        # Prepare input arrays
        if not isinstance(gen, tuple):
            gen = (gen,) * n
        data0 = tuple([g(*a) for g, a in zip(gen, args)])
        data1 = tuple([_.copy() for _ in data0])

        # Invoke non-fused function
        try:
            ret0 = func(*data0)  # Non-fused
            err0 = None
        except Exception as e:
            if type(e) not in error_types:
                raise
            ret0 = None
            err0 = e

        # Invoke fused function
        try:
            ret1 = f(*data1)  # Fused
            err1 = None
        except Exception as e:
            if type(e) not in error_types:
                raise
            ret1 = None
            err1 = e

        self.assertEqual(err0 is None, err1 is None)
        if err0 is not None:
            # Error
            self.assertEqual(type(err0), type(err1))
            self.assertEqual(str(err0), str(err1))
            arrs0 = None
            arrs1 = None
        else:
            # Success
            self.assertEqual(ret0 is None, ret1 is None)
            if ret0 is None:
                # Both return values are None
                ret0 = ()
                ret1 = ()
            else:
                # Return values must have the same type
                self.assertEqual(type(ret0), type(ret1))

                if not isinstance(ret0, tuple):
                    # Single arrays are returned
                    ret0 = (ret0,)
                    ret1 = (ret1,)
                else:
                    # Tuples are returned
                    self.assertEqual(len(ret0), len(ret1))

            # Concatenate return values and input arrays
            arrs0 = ret0 + data0
            arrs1 = ret1 + data1

            # Test they have same values
            for nf, f in zip(arrs0, arrs1):
                numpy.testing.assert_array_almost_equal(nf.get(), f.get())

        return err0 is not None, (arrs0, arrs1)

    def check_reduce(self, func, n, reduce_f, gen, args=None):
        if args is None:
            args = ((),) * n
        self._check_reduce(func, n, reduce_f, gen, args)

    def _check_reduce(self, func, n, reduce_f, gen, args):
        @cupy.fuse()
        def f(*args):
            return reduce_f(func(*args))

        data = [gen(*a) for a in args]
        ret0 = reduce_f(func(*data))  # Non-fused
        ret1 = f(*data)  # Fused
        numpy.testing.assert_array_almost_equal(ret0.get(), ret1.get())

    def test_setitem_ellipsis(self):
        def func(x, y):
            y[...] = x
            return y

        ret = self._check(
            func, 2, self.random_int, ((2, 3),) * 2,
            error_types=(TypeError,))
        is_err, (arrs_n, arrs_f) = ret

        if not is_err:
            # The returned array must equal to z
            ret, x, y = arrs_f
            testing.assert_array_equal(x, ret)
            testing.assert_array_equal(x, y)

    def test_setitem_none_slice(self):
        def func(x, y):
            y[:] = x
            return y

        ret = self._check(
            func, 2, self.random_int, ((2, 3),) * 2,
            error_types=(TypeError,))
        is_err, (arrs_n, arrs_f) = ret

        if not is_err:
            # The returned array must equal to z
            ret, x, y = arrs_f
            testing.assert_array_equal(x, ret)
            testing.assert_array_equal(x, y)

    @testing.for_all_dtypes_combination(
        names=['src_dtype', 'dst_dtype'], full=True, no_complex=True)
    def test_out_arg(self, src_dtype, dst_dtype):

        def func(x, y, z):
            return cupy.add(x, y, out=z)

        dtypes = (src_dtype, src_dtype, dst_dtype)
        ret = self._check(
            func, 3,
            lambda iarg: cupy.arange(6).astype(dtypes[iarg]).reshape((2, 3)),
            [(_,) for _ in range(3)],
            error_types=(TypeError,))
        is_err, (arrs_n, arrs_f) = ret

        if not is_err:
            # The returned array must equal to z
            arr_ret = arrs_f[0]
            arr_z = arrs_f[3]
            testing.assert_array_equal(arr_ret, arr_z)

    def test_out_arg2(self):

        def func(x, y, z, u, v):
            cupy.add(x, y, out=z)
            cupy.subtract(z, x, out=u)
            cupy.multiply(z, x, out=v)
            return u

        ret = self._check(
            func, 5, self.random_int, ((),) * 5,
            error_types=(TypeError,))
        is_err, (arrs_n, arrs_f) = ret

        # Must succeed
        self.assertFalse(is_err)

        # The returned array must equal to u
        arr_ret = arrs_f[0]
        arr_u = arrs_f[4]
        testing.assert_array_equal(arr_ret, arr_u)

    def test_bitwise(self):
        self.check(cupy.bitwise_and, 2, self.random_int)
        self.check(cupy.bitwise_or, 2, self.random_int)
        self.check(cupy.bitwise_xor, 2, self.random_int)
        self.check(cupy.invert, 1, self.random_int)
        self.check(cupy.left_shift, 2, self.random_int, ((0, 20),) * 2)
        self.check(cupy.right_shift, 2, self.random_int, ((0, 20),) * 2)

    def test_compare(self):
        self.check(cupy.greater, 2, self.random_int)
        self.check(cupy.greater_equal, 2, self.random_int)
        self.check(cupy.less, 2, self.random_int)
        self.check(cupy.less_equal, 2, self.random_int)
        self.check(cupy.equal, 2, self.random_int)
        self.check(cupy.not_equal, 2, self.random_int)

    def test_logic_content(self):
        self.check(cupy.isfinite, 1, self.random_real)
        self.check(cupy.isinf, 1, self.random_real)
        self.check(cupy.isnan, 1, self.random_real)

    def test_logic_ops(self):
        self.check(cupy.logical_and, 2, self.random_int, ((0, 2),) * 2)
        self.check(cupy.logical_or, 2, self.random_int, ((0, 2),) * 2)
        self.check(cupy.logical_not, 1, self.random_int, ((0, 2),))
        self.check(cupy.logical_xor, 2, self.random_int, ((0, 2),) * 2)

    def test_trigonometric(self):
        self.check(cupy.sin, 1, self.random_real)
        self.check(cupy.cos, 1, self.random_real)
        self.check(cupy.tan, 1, self.random_real)
        self.check(cupy.arcsin, 1, self.random_real, ((-1, 1),))
        self.check(cupy.arccos, 1, self.random_real, ((-1, 1),))
        self.check(cupy.arctan, 1, self.random_real)
        self.check(cupy.hypot, 2, self.random_real)
        self.check(cupy.deg2rad, 1, self.random_real)
        self.check(cupy.rad2deg, 1, self.random_real)
        self.check(cupy.degrees, 1, self.random_real)
        self.check(cupy.radians, 1, self.random_real)

    def test_hyperbolic(self):
        self.check(cupy.sinh, 1, self.random_real, ((-10, 10),))
        self.check(cupy.cosh, 1, self.random_real, ((-10, 10),))
        self.check(cupy.tanh, 1, self.random_real, ((-10, 10),))
        self.check(cupy.arcsinh, 1, self.random_real, ((-10, 10),))
        self.check(cupy.arccosh, 1, self.random_real, ((1, 10),))
        self.check(cupy.arctanh, 1, self.random_real, ((0, 1),))

    def test_rounding(self):
        self.check(cupy.rint, 1, self.random_real)
        self.check(cupy.floor, 1, self.random_real)
        self.check(cupy.ceil, 1, self.random_real)
        self.check(cupy.trunc, 1, self.random_real)

    def test_explog(self):
        self.check(cupy.exp, 1, self.random_real, ((-10, 10),))
        self.check(cupy.expm1, 1, self.random_real, ((-10, 10),))
        self.check(cupy.exp2, 1, self.random_real, ((-10, 10),))
        self.check(cupy.log, 1, self.random_real, ((0, 10),))
        self.check(cupy.log10, 1, self.random_real, ((0, 10),))
        self.check(cupy.log2, 1, self.random_real, ((0, 10),))
        self.check(cupy.log1p, 1, self.random_real, ((-1, 10),))
        self.check(cupy.logaddexp, 2, self.random_real, ((0, 10),) * 2)
        self.check(cupy.logaddexp2, 2, self.random_real, ((0, 10),) * 2)

    def test_special_func(self):
        self.check(cupy.i0, 1, self.random_real)
        self.check(cupy.sinc, 1, self.random_real)

    def test_floating(self):
        self.check(cupy.signbit, 1, self.random_real)
        self.check(cupy.copysign, 2, self.random_real)
        self.check(cupy.ldexp, 2, self.random_int, ((1, 10),) * 2)
        self.check(cupy.frexp, 1, self.random_real, ((1, 1000),))
        self.check(cupy.nextafter, 2, self.random_real)

    def test_arithmetic(self):
        self.check(cupy.add, 2, self.random_real)
        self.check(cupy.reciprocal, 1, self.random_real)
        self.check(cupy.negative, 1, self.random_real)
        self.check(cupy.angle, 1, self.random_imag)
        self.check(cupy.conj, 1, self.random_imag)
        self.check(cupy.real, 1, self.random_imag)
        self.check(cupy.imag, 1, self.random_imag)
        self.check(cupy.multiply, 2, self.random_real)
        self.check(cupy.divide, 2, self.random_real)
        self.check(cupy.power, 2, self.random_real, ((0, 10),) * 2)
        self.check(cupy.subtract, 2, self.random_real)
        self.check(cupy.true_divide, 2, self.random_int, ((1, 1000),) * 2)
        self.check(cupy.floor_divide, 2, self.random_real, ((1, 1000),) * 2)
        self.check(cupy.fmod, 2, self.random_real)
        self.check(cupy.mod, 2, self.random_int, ((1, 1000),) * 2)
        self.check(cupy.modf, 1, self.random_real)
        self.check(cupy.remainder, 2, self.random_int, ((1, 1000),) * 2)

    @testing.with_requires('numpy>=1.13')
    def test_divmod(self):
        self.check(cupy.divmod, 2, self.random_real)

    def test_misc(self):
        self.check(cupy.sqrt, 1, self.random_real, ((0, 1000),))
        self.check(cupy.cbrt, 1, self.random_real, ((0, 1000),))
        self.check(cupy.square, 1, self.random_real)
        self.check(cupy.absolute, 1, self.random_real)
        self.check(cupy.abs, 1, self.random_real)
        self.check(cupy.sign, 1, self.random_real)
        self.check(cupy.maximum, 2, self.random_real)
        self.check(cupy.minimum, 2, self.random_real)
        self.check(cupy.fmax, 2, self.random_real)
        self.check(cupy.fmin, 2, self.random_real)

    def test_special(self):
        self.check(cupy.where, 3,
                   (self.random_bool,
                    lambda *args: self.random_int(*args, seed=0),
                    lambda *args: self.random_int(*args, seed=1)),
                   ((), (0, 100), (0, 100)))
        self.check(cupy.clip, 3,
                   (lambda *args: self.random_real(*args, seed=0),
                    lambda *args: self.random_real(*args, seed=1),
                    lambda *args: self.random_real(*args, seed=2)),
                   ((0, 1000), (0, 500), (500, 1000)))
        self.check(cupy.around, 2,
                   (self.random_bool,
                    self.random_int,
                    self.random_real))

    def test_reduce(self):
        self.check_reduce(cupy.bitwise_and, 2, cupy.sum, self.random_int)
        self.check_reduce(cupy.sqrt, 1, cupy.prod, self.random_int, ((1, 2),))
        self.check_reduce(cupy.sqrt, 1, cupy.prod, self.random_real, ((1, 2),))

        self.check_reduce(lambda x: x, 1, cupy.amax, self.random_int)
        self.check_reduce(lambda x: x, 1, cupy.amin, self.random_int)

        self.check_reduce(lambda x: x, 1, cupy.all, self.random_bool)
        self.check_reduce(lambda x: x, 1, cupy.any, self.random_bool)


@testing.gpu
class TestFusionMisc(unittest.TestCase):

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_allclose(atol=1e-5)
    def check_unary(self, name, xp, dtype, no_bool=False):
        if no_bool and numpy.dtype(dtype).char == '?':
            return numpy.int_(0)
        a = testing.shaped_arange((2, 3), xp, dtype)

        @cupy.fuse()
        def g(x):
            return getattr(xp, name)(x)

        return g(a)

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_allclose(atol=1e-5)
    def check_binary(self, name, xp, dtype, no_bool=False):
        if no_bool and numpy.dtype(dtype).char == '?':
            return numpy.int_(0)
        a = testing.shaped_arange((2, 3), xp, dtype)
        b = testing.shaped_reverse_arange((2, 3), xp, dtype)

        @cupy.fuse()
        def g(x, y):
            return getattr(xp, name)(x, y)
        return g(a, b)

    @testing.for_dtypes(['?', 'b', 'h', 'i', 'q', 'e', 'f', 'd'])
    @testing.numpy_cupy_allclose(atol=1e-5)
    def check_unary_negative(self, name, xp, dtype, no_bool=False):
        if no_bool and numpy.dtype(dtype).char == '?':
            return numpy.int_(0)
        a = xp.array([-3, -2, -1, 1, 2, 3], dtype=dtype)

        @cupy.fuse()
        def g(x):
            return getattr(xp, name)(x)

        return g(a)

    @testing.for_float_dtypes()
    @testing.numpy_cupy_array_equal()
    @fusion_default_array_equal()
    def check_binary_nan(self, name, xp, dtype):
        a = xp.array([-3, numpy.NAN, -1, numpy.NAN, 0, numpy.NAN, 2],
                     dtype=dtype)
        b = xp.array([numpy.NAN, numpy.NAN, 1, 0, numpy.NAN, -1, -2],
                     dtype=dtype)
        return a, b

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_array_equal()
    def test_external_clip(self, xp, dtype):
        a = testing.shaped_arange((2, 3, 4), xp, dtype)

        @cupy.fuse()
        def g(x, y, z):
            return xp.clip(x, y, z)

        ty = numpy.dtype(dtype).type
        return g(a, ty(3), ty(13))

    @testing.with_requires('numpy>=1.11.2')
    def test_sqrt(self):
        # numpy.sqrt is broken in numpy<1.11.2
        self.check_unary('sqrt')

    @testing.with_requires('numpy>=1.10')
    def test_cbrt(self):
        self.check_unary('cbrt')

    def test_square(self):
        self.check_unary('square')

    def test_absolute(self):
        self.check_unary('absolute')

    def test_absolute_negative(self):
        self.check_unary_negative('absolute')

    def test_sign(self):
        self.check_unary('sign', no_bool=True)

    def test_sign_negative(self):
        self.check_unary_negative('sign', no_bool=True)

    def test_maximum(self):
        self.check_binary('maximum')

    def test_maximum_nan(self):
        self.check_binary_nan('maximum')

    def test_minimum(self):
        self.check_binary('minimum')

    def test_minimum_nan(self):
        self.check_binary_nan('minimum')

    def test_fmax(self):
        self.check_binary('fmax')

    def test_fmax_nan(self):
        self.check_binary_nan('fmax')

    def test_fmin(self):
        self.check_binary('fmin')

    def test_fmin_nan(self):
        self.check_binary_nan('fmin')

    @testing.for_all_dtypes_combination(
        names=['src_dtype'], no_complex=True)
    @testing.for_all_dtypes_combination(
        names=['dst_dtype'])
    @testing.numpy_cupy_array_equal()
    def test_astype_class(self, xp, src_dtype, dst_dtype):

        @cupy.fuse()
        def f(x):
            return x.astype(dst_dtype)

        x = xp.arange(6).astype(src_dtype).reshape(2, 3)
        return f(x)


@testing.gpu
class TestFusionFuse(unittest.TestCase):

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_array_equal()
    def test_fuse1(self, xp, dtype):
        a = xp.array([2, 2, 2, 2, 3, 3, 3, 3], dtype=dtype)
        b = xp.array([2, 2, 3, 3, 2, 2, 3, 3], dtype=dtype)
        c = xp.array([2, 3, 2, 3, 2, 3, 2, 3], dtype=dtype)

        @cupy.fuse()
        def g(x, y, z):
            w = x * y + z
            (x, w) = (w, x)
            return z * w + y + x

        return g(a, b, c)

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_array_equal()
    def test_fuse2(self, xp, dtype):
        a = xp.array([2, 2, 2, 2, 3, 3, 3, 3], dtype=dtype)
        b = xp.array([2, 2, 3, 3, 2, 2, 3, 3], dtype=dtype)
        c = xp.array([2, 3, 2, 3, 2, 3, 2, 3], dtype=dtype)

        @cupy.fuse()
        def g(x, y, z):
            x += z
            xp.add(x, y, z)
            return z

        return g(a, b, c)

    @testing.for_all_dtypes(no_bool=True, no_complex=True)
    @testing.numpy_cupy_array_equal()
    def test_fuse3(self, xp, dtype):
        a = xp.array([2, 2, 2, 2, 3, 3, 3, 3], dtype=dtype)
        b = xp.array([2, 2, 3, 3, 2, 2, 3, 3], dtype=dtype)
        c = xp.array([2, 3, 2, 3, 2, 3, 2, 3], dtype=dtype)

        @cupy.fuse()
        def g(x, y, z):
            x = 10 + (-x) * (x - y) + 10
            x = 2 * (100 - x - 30)
            x = x / (y + 1 / y)
            return z // x + x // z + 100 // x + 100 // z

        return g(a, b, c)

    @testing.for_int_dtypes()
    @testing.numpy_cupy_array_equal()
    def test_fuse4(self, xp, dtype):
        a = xp.array([2, 2, 2, 2, 3, 3, 3, 3], dtype=dtype)
        b = xp.array([2, 2, 3, 3, 2, 2, 3, 3], dtype=dtype)
        c = xp.array([2, 3, 2, 3, 2, 3, 2, 3], dtype=dtype)

        @cupy.fuse()
        def g(x, y, z):
            x = x * y % z + 10 % x << x << y >> z
            return x + (1 << y) + (1 << z) + (120 >> y) + (120 >> y)

        return g(a, b, c)

    @testing.for_int_dtypes(no_bool=True)
    @testing.numpy_cupy_array_equal()
    def test_fuse5(self, xp, dtype):
        a = xp.arange(15, dtype=dtype)
        b = a * a[::-1]
        a = a * 3 + 11
        c = (a * b) % 63

        @cupy.fuse()
        def g(x, y, z):
            x = ~(x & y) | (x ^ z) ^ (z | y)
            y = 109 & y
            z = 109 | z
            z = 88 ^ z
            return x + y + z

        return g(a, b, c)

    @testing.for_int_dtypes(no_bool=True)
    @testing.numpy_cupy_array_equal()
    def test_fuse6(self, xp, dtype):
        a = xp.arange(15, dtype=dtype)
        b = a * a[::-1]
        a = a * 3 + 11
        c = (a * b) % 63

        @cupy.fuse()
        def g(x, y, z):
            x = ~(x & y) | (x ^ z) ^ (z | y)
            y &= 109
            z |= 109
            z ^= 88
            return x + y + z

        return g(a, b, c)

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_array_equal()
    def test_fuse7(self, xp, dtype):
        a = xp.array([2, 2, 2, 2, 3, 3, 3, 3], dtype=dtype)
        b = xp.array([2, 2, 3, 3, 2, 2, 3, 3], dtype=dtype)
        c = xp.array([2, 3, 2, 3, 2, 3, 2, 3], dtype=dtype)

        def toi(x):
            return xp.where(x, 1, 0)

        @cupy.fuse()
        def g(p, q, r, s, t, u):
            x = toi(p == q) + toi(r < s) + toi(t > u)
            x += toi(p != r) + toi(q <= t) + toi(s >= u)
            return x

        return g(a, b, c, a, b, c)

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_array_equal()
    def test_fuse8(self, xp, dtype):
        a = xp.array([2, 2, 2, 2, 3, 3, 3, 3], dtype=dtype)
        b = xp.array([2, 2, 3, 3, 2, 2, 3, 3], dtype=dtype)
        c = xp.array([2, 3, 2, 3, 2, 3, 2, 3], dtype=dtype)

        def toi(x):
            return xp.where(x, 1, 0)

        @cupy.fuse()
        def g(p, q, r):
            x = toi(2 == p) + toi(2 != q) + toi(3 > r)
            y = toi(2 < p) + toi(2 >= q) + toi(3 <= r)
            return x + y << 3

        return g(a, b, c)

    @testing.for_all_dtypes(no_bool=True, no_complex=True)
    @testing.numpy_cupy_array_equal()
    def test_fuse9(self, xp, dtype):
        a = xp.array([2, 2, 2, 2, 3, 3, 3, 3], dtype=dtype)
        b = xp.array([2, 2, 3, 3, 2, 2, 3, 3], dtype=dtype)
        c = xp.array([2, 3, 2, 3, 2, 3, 2, 3], dtype=dtype)

        @cupy.fuse()
        def g(x, y, z):
            x *= y
            x += y
            x = x / y
            z %= y
            x += y + z

        g(a, b, c)
        return a

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_array_equal()
    def test_fuse10(self, xp, dtype):
        a = xp.array([2, 2, 2, 2, 3, 3, 3, 3], dtype=dtype)
        b = xp.array([2, 2, 3, 3, 2, 2, 3, 3], dtype=dtype)
        c = xp.array([2, 3, 2, 3, 2, 3, 2, 3], dtype=dtype)

        @cupy.fuse()
        def g(x, y, z):
            a = x
            a += y
            xp.add(x, y, z)

        g(a, b, c)
        return c

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_array_equal()
    def test_fuse11(self, xp, dtype):
        a = xp.array([2, 2, 2, 2, 3, 3, 3, 3], dtype=dtype)
        b = xp.array([2, 2, 3, 3, 2, 2, 3, 3], dtype=dtype)
        c = xp.array([2, 3, 2, 3, 2, 3, 2, 3], dtype=dtype)

        @cupy.fuse()
        def g(x, y, z):
            a = x
            a += y
            xp.add(x, y, z)
            return y

        res = g(a, b, c)
        return c + res

    # NumPy 1.9 accepts itruediv between integers
    @testing.with_requires('numpy>=1.10')
    @unittest.skipUnless(six.PY3, 'Only for py3')
    @testing.for_int_dtypes()
    @testing.numpy_cupy_raises()
    def test_fuse_int_itruediv_py3_raises(self, xp, dtype):
        a = xp.array(3, dtype=dtype)
        b = xp.array(2, dtype=dtype)

        @cupy.fuse()
        def g(x, y):
            x /= y

        g(a, b)

    @testing.for_all_dtypes(no_bool=True)
    @testing.numpy_cupy_array_equal()
    def test_different_type_same_ufunc(self, xp, dtype):
        a = xp.array([2, 2, 2, 2, 3, 3, 3, 3], dtype=dtype)
        b = xp.array([2, 2, 3, 3, 2, 2, 3, 3], dtype=numpy.int32)
        c = xp.array([2, 3, 2, 3, 2, 3, 2, 3], dtype=numpy.float32)

        @cupy.fuse()
        def g(x, y, z):
            return (x + y, y + z, z + x)

        s, t, u = g(a, b, c)
        return s

    @unittest.skipUnless(six.PY2, 'Only for py2')
    @testing.for_int_dtypes(no_bool=True)
    @testing.numpy_cupy_array_equal()
    def test_fuse_int_ifloordiv_py2(self, xp, dtype):
        a = xp.array(3, dtype=dtype)
        b = xp.array(2, dtype=dtype)

        @cupy.fuse()
        def g(x, y):
            x /= y

        g(a, b)
        return a

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_array_equal()
    def test_reduce1(self, xp, dtype):
        a = xp.array([[2, 2, 2, 2], [3, 3, 3, 3]], dtype=dtype)
        b = xp.array([[2, 2, 3, 3], [2, 2, 3, 3]], dtype=dtype)
        c = xp.array([[2, 3, 2, 3], [2, 3, 2, 3]], dtype=dtype)

        @cupy.fuse()
        def g(x, y, z):
            return xp.sum(x * y + z)

        return g(a, b, c)

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_array_equal()
    def test_reduce2(self, xp, dtype):
        a = xp.array([[2, 2, 2, 2], [3, 3, 3, 3]], dtype=dtype)
        b = xp.array([[2, 2, 3, 3], [2, 2, 3, 3]], dtype=dtype)
        c = xp.array([[2, 3, 2, 3], [2, 3, 2, 3]], dtype=dtype)

        @cupy.fuse()
        def g(x, y, z):
            return xp.sum(x * y + z, axis=0)

        return g(a, b, c)

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_array_equal()
    def test_reduce3(self, xp, dtype):
        a = xp.array([[2, 2, 2, 2], [3, 3, 3, 3]], dtype=dtype)
        b = xp.array([[2, 2, 3, 3], [2, 2, 3, 3]], dtype=dtype)
        c = xp.array([[2, 3, 2, 3], [2, 3, 2, 3]], dtype=dtype)

        @cupy.fuse()
        def g(x, y, z):
            return xp.sum(x * y + z, axis=1)

        return g(a, b, c)

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_array_equal()
    def test_reduce4(self, xp, dtype):
        a = xp.array([[2, 2, 2, 2], [3, 3, 3, 3]], dtype=dtype)

        @cupy.fuse()
        def g(x):
            return xp.prod(x)

        return g(a)

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_array_equal()
    def test_reduce5(self, xp, dtype):
        a = xp.array([[2, 2, 2, 2], [3, 3, 3, 3]], dtype=dtype)

        @cupy.fuse()
        def g(x):
            return xp.max(x, axis=0)

        return g(a)

    @testing.for_all_dtypes(no_complex=True)
    @testing.numpy_cupy_array_equal()
    def test_reduce6(self, xp, dtype):
        a = xp.array([[2, 2, 2, 2], [3, 3, 3, 3]], dtype=dtype)

        @cupy.fuse()
        def g(x):
            return xp.min(x, axis=0)

        return g(a)


@testing.gpu
class TestFusionDecorator(unittest.TestCase):
    @testing.numpy_cupy_array_equal()
    def test_without_paren(self, xp):
        @cupy.fuse
        def func_wo_paren(x):
            """Fuse without parentheses"""
            return x + x

        self.assertEqual(func_wo_paren.__name__, 'func_wo_paren')
        self.assertEqual(func_wo_paren.__doc__, 'Fuse without parentheses')

        a = xp.array([1])
        return func_wo_paren(a)

    @testing.numpy_cupy_array_equal()
    def test_with_paren(self, xp):
        @cupy.fuse()
        def func_w_paren(x):
            """Fuse with parentheses"""
            return x + x

        self.assertEqual(func_w_paren.__name__, 'func_w_paren')
        self.assertEqual(func_w_paren.__doc__, 'Fuse with parentheses')

        a = xp.array([1])
        return func_w_paren(a)


@testing.gpu
class TestFusionKernelName(unittest.TestCase):

    def check(self, xp, func, expected_name, is_elementwise):
        a = xp.arange(0, 12, dtype='d').reshape(3, 4)
        b = xp.arange(5, 17, dtype='d').reshape(3, 4)
        c = xp.arange(13, 25, dtype='d').reshape(3, 4)

        # Test kernel name (with mock)
        if xp is cupy:
            target = (
                'cupy.core._kernel.ElementwiseKernel' if is_elementwise
                else 'cupy.core._kernel.ReductionKernel')

            with mock.patch(target) as Kernel:
                func(a, b, c)
                Kernel.assert_called_once()
                self.assertEqual(Kernel.call_args[1]['name'], expected_name)

        # Test there's no error in computation (without mock)
        return func(a, b, c)

    @testing.numpy_cupy_allclose(atol=1e-5)
    def test_elementwise(self, xp):
        def func(a, b, c):
            @cupy.fuse()
            def func_a1(x, y, z):
                return (x + y) * z

            return func_a1(a, b, c)

        return self.check(xp, func, 'func_a1', True)

    @testing.numpy_cupy_allclose(atol=1e-5)
    def test_elementwise_with_name(self, xp):
        def func(a, b, c):
            @cupy.fuse(kernel_name='abc')
            def func_a1(x, y, z):
                return (x + y) * z

            return func_a1(a, b, c)

        return self.check(xp, func, 'abc', True)

    @testing.numpy_cupy_allclose(atol=1e-5)
    def test_reduction_premap(self, xp):
        def func(a, b, c):
            @cupy.fuse()
            def func_a1(x, y, z):
                return xp.sum((x + y) * z)

            return func_a1(a, b, c)

        return self.check(xp, func, 'func_a1', False)

    @testing.numpy_cupy_allclose(atol=1e-5)
    def test_reduction_postmap(self, xp):
        def func(a, b, c):
            @cupy.fuse()
            def func_a1(x):
                return xp.sqrt(xp.sum(x) + 10)

            return func_a1(a)

        return self.check(xp, func, 'func_a1', False)

    @testing.numpy_cupy_allclose(atol=1e-5)
    def test_reduction_01(self, xp):
        def func(a, b, c):
            @cupy.fuse()
            def func_a1(x, y, z):
                return xp.sqrt(xp.prod(x + y * z, axis=1) + 10)

            return func_a1(a, b, c)

        return self.check(xp, func, 'func_a1', False)

    @testing.numpy_cupy_allclose(atol=1e-5)
    def test_reduction_with_name(self, xp):
        def func(a, b, c):
            @cupy.fuse(kernel_name='abc')
            def func_a1(x, y, z):
                return xp.sum((x + y) * z)

            return func_a1(a, b, c)

        return self.check(xp, func, 'abc', False)


@testing.gpu
class TestFusionScalar(unittest.TestCase):

    @testing.for_all_dtypes_combination(names=['dtype1', 'dtype2'])
    @testing.numpy_cupy_array_equal()
    def test_python_scalar(self, xp, dtype1, dtype2):

        @cupy.fuse()
        def f(x):
            return x * dtype2(1).item()
        return f(testing.shaped_arange((1,), xp, dtype1))

    @testing.for_all_dtypes_combination(names=['dtype1', 'dtype2'])
    @testing.numpy_cupy_array_equal()
    def test_numpy_scalar(self, xp, dtype1, dtype2):

        @cupy.fuse()
        def f(x):
            return x * dtype2(1)
        return f(testing.shaped_arange((1,), xp, dtype1))

    @testing.for_all_dtypes_combination(names=('dtype1', 'dtype2'))
    @testing.numpy_cupy_array_equal()
    def test_param_python_scalar(self, xp, dtype1, dtype2):

        @cupy.fuse()
        def f(x, y):
            return x + y
        x = testing.shaped_arange((10,), xp, dtype1)
        y = dtype2(1).item()
        return f(x, y)

    @testing.for_all_dtypes_combination(names=('dtype1', 'dtype2'))
    @testing.numpy_cupy_array_equal()
    def test_param_numpy_scalar(self, xp, dtype1, dtype2):

        @cupy.fuse()
        def f(x, y):
            return x + y
        x = testing.shaped_arange((10,), xp, dtype1)
        y = dtype2(1)
        return f(x, y)

    @testing.for_all_dtypes_combination(names=('dtype1', 'dtype2'))
    @testing.numpy_cupy_array_equal()
    def test_param_numpy_scalar_binop(self, xp, dtype1, dtype2):

        @cupy.fuse()
        def f(x, y, z):
            dtype = (x + y).dtype
            return z.astype(dtype)
        x = dtype1(1)
        y = dtype2(1)
        z = xp.zeros(10)
        return f(x, y, z)

    @testing.for_all_dtypes()
    @testing.numpy_cupy_array_equal()
    def test_broadcastable(self, xp, dtype):

        @cupy.fuse()
        def f(x, y):
            z = x
            x += y
            return x + z

        x = testing.shaped_arange((4, 4), xp, dtype)
        y = testing.shaped_arange((4,), xp, dtype)
        return f(x, y)

    @testing.for_all_dtypes()
    @testing.numpy_cupy_raises()
    def test_non_broadcastable(self, xp, dtype):

        @cupy.fuse()
        def f(x, y):
            z = x
            x += y
            return x + z

        x = testing.shaped_arange((4,), xp, dtype)
        y = testing.shaped_arange((4, 4), xp, dtype)
        return f(x, y)

    @testing.for_all_dtypes()
    @testing.numpy_cupy_array_equal()
    def test_scalar_update_with_broadcast(self, xp, dtype):

        @cupy.fuse()
        def f(x, y):
            z = x
            x += y
            return x + z

        x = numpy.dtype(dtype).type(1)
        y = testing.shaped_arange((4, 4), xp, dtype)
        return f(x, y)


@testing.gpu
class TestFusionNone(unittest.TestCase):

    @testing.for_all_dtypes()
    @testing.numpy_cupy_array_equal()
    def test_python_none_parameter(self, xp, dtype):

        @cupy.fuse()
        def f(x, y, z):
            if y is None:
                return x * z
            return x + y + z

        x = testing.shaped_arange((10,), xp, dtype)
        y = testing.shaped_arange((10,), xp, dtype)
        z = testing.shaped_arange((10,), xp, dtype)
        return f(x, None, z) + f(x, y, z)


@testing.gpu
class TestFusionReturnsConstantValue(unittest.TestCase):

    @testing.for_all_dtypes()
    @testing.numpy_cupy_array_equal()
    def test_pass(self, xp, dtype):

        @cupy.fuse()
        def f(x):
            pass

        x = testing.shaped_arange((3, 3), xp, dtype)
        y = f(x)
        self.assertEqual(y, None)
        return x

    @testing.for_all_dtypes(no_bool=True)
    @testing.numpy_cupy_array_equal()
    def test_no_retval(self, xp, dtype):

        @cupy.fuse()
        def f(x):
            x += 1

        x = testing.shaped_arange((3, 3), xp, dtype)
        y = f(x)
        self.assertEqual(y, None)
        return x


@testing.gpu
class TestFusionReturnsTuple(unittest.TestCase):

    @testing.for_all_dtypes()
    @testing.numpy_cupy_array_list_equal()
    def test_empty_tuple(self, xp, dtype):

        @cupy.fuse()
        def f(x):
            return ()

        x = testing.shaped_arange((3, 4), xp, dtype)
        y = f(x)
        self.assertEqual(type(y), tuple)
        return y

    @testing.for_all_dtypes()
    @testing.numpy_cupy_array_list_equal()
    def test_singleton_tuple(self, xp, dtype):

        @cupy.fuse()
        def f(x):
            return x * 2,

        x = testing.shaped_arange((3, 4), xp, dtype)
        y = f(x)
        self.assertEqual(type(y), tuple)
        return y

    @testing.for_all_dtypes()
    @testing.numpy_cupy_array_list_equal()
    def test_pair_tuple(self, xp, dtype):

        @cupy.fuse()
        def f(x):
            return x * 2, x * 3

        x = testing.shaped_arange((3, 4), xp, dtype)
        y = f(x)
        self.assertEqual(type(y), tuple)
        return y


class TestFusionComposition(unittest.TestCase):

    @testing.for_all_dtypes(no_bool=True)
    @testing.numpy_cupy_array_equal()
    def test_composition(self, xp, dtype):
        @cupy.fuse()
        def f(x, y):
            return x - y * 2, x + y

        @cupy.fuse()
        def g(x, y, z):
            a, b = f(x + z, z - x * 3)
            c, d = f(x - y, y - z)
            return a + b * c - d

        @cupy.fuse()
        def h(x, y):
            a, b = f(x + y * 2, y * 3)
            return a - b * g(x - 2, x - 3, -y)

        x = testing.shaped_arange((3, 3), xp, dtype)
        y = testing.shaped_arange((3, 3), xp, dtype)
        return h(x, y)


class TestFusionCompile(unittest.TestCase):

    # TODO(asi1024): Support it

    # @testing.for_all_dtypes(no_bool=True)
    # @testing.numpy_cupy_array_equal()
    # def test_compile_from_dtypes(self, xp, dtype):
    #     @cupy.fuse()
    #     def f(x, y):
    #         return x - y * 2

    #     x = testing.shaped_arange((3, 3), xp, dtype)
    #     y = testing.shaped_arange((3, 3), xp, dtype)
    #     f._compile_from_dtypes(x.dtype, y.dtype)
    #     return f(x, y)

    @testing.for_all_dtypes(no_bool=True)
    @testing.numpy_cupy_array_equal()
    def test_clear_cache(self, xp, dtype):
        @cupy.fuse()
        def f(x, y):
            return x - y * 2

        x = testing.shaped_arange((3, 3), xp, dtype)
        y = testing.shaped_arange((3, 3), xp, dtype)
        f.clear_cache()
        return f(x, y)


@testing.gpu
class TestFusionGetArrayModule(unittest.TestCase):

    @testing.for_all_dtypes()
    @testing.numpy_cupy_array_equal()
    def test_get_array_module(self, xp, dtype):

        @cupy.fuse()
        def f(x):
            xp = cupy.get_array_module(x)
            return xp.square(x)

        x = testing.shaped_arange((3, 4), xp, dtype)
        return f(x)


class TestFusionThread(unittest.TestCase):

    def test_thread(self):
        x = testing.shaped_arange((3, 3), cupy, cupy.int64)
        y = testing.shaped_arange((3, 3), cupy, cupy.int64)
        out = [None]

        @cupy.fuse()
        def f(x, y):
            return x + y * 2

        def _target(x, y):
            cupy.cuda.Device(0).use()
            out[0] = f(x, y)

        t = threading.Thread(target=_target, args=(x, y))
        t.daemon = True
        t.start()
        t.join()
        assert (out[0] == f(x, y)).all()

    @testing.numpy_cupy_array_equal()
    def test_thread_multiple_dtypes(self, xp):
        x1 = testing.shaped_arange((3, 3), xp, xp.int64)
        y1 = testing.shaped_arange((3, 3), xp, xp.int64)
        x2 = x1.astype(xp.float64)
        y2 = y1.astype(xp.float64)
        threads = [None] * 100
        out = [None] * 100

        @cupy.fuse()
        def f(x, y):
            return x + y * 2

        def _target(tid, x, y):
            if xp is cupy:
                xp.cuda.Device(0).use()
            out[tid] = f(x, y).astype(xp.int64)

        def run_thread(tid):
            x, y = (x1, y1) if tid % 2 == 0 else (x2, y2)
            t = threading.Thread(target=_target, args=(tid, x, y))
            threads[tid] = t
            t.daemon = True
            t.start()

        for tid in six.moves.range(0, 50):
            run_thread(tid)

        for tid in six.moves.range(0, 50):
            threads[tid].join()

        for tid in six.moves.range(50, 100):
            run_thread(tid)

        for tid in six.moves.range(50, 100):
            threads[tid].join()

        return xp.concatenate(out)


@testing.gpu
class TestBroadcast(unittest.TestCase):

    @testing.numpy_cupy_array_equal()
    def test_broadcast(self, xp):

        @cupy.fuse()
        def f(x, y):
            x += y
            return x

        x = testing.shaped_arange((2, 3, 4), xp, xp.int64)
        y = testing.shaped_arange((3, 4), xp, xp.int64)
        return f(x, y)

    @testing.numpy_cupy_raises()
    def test_broadcast_datarace(self, xp):

        @cupy.fuse()
        def f(x, y):
            x += y
            return x

        x = testing.shaped_arange((3, 4), xp, xp.int64)
        y = testing.shaped_arange((2, 3, 4), xp, xp.int64)
        return f(x, y)

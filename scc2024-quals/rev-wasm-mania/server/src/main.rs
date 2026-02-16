use leptos::*;
use arc4::*;
use leptos::prelude::*;

fn main() {
    mount_to_body(|| {
        view! {
            <FlagChecker
                initial_value="SCC{}".to_owned()
            />
        }
    })
}

fn string_to_bytes(s: String) -> Vec<u8>
{
    s.bytes().collect::<Vec<_>>()
}

fn bytes_to_string(data: Vec<u8>) -> String
{
    match String::from_utf8(data)
    {
        Ok(s) => s,
        Err(_) => String::new(),
    }
}

fn new_rc4<'a>(key: &'a [u8]) -> Arc4<'a> //StreamCipherCoreWrapper<Rc4Core<UInt<UInt<UInt<UInt<UTerm, B1>, B0>, B0>, B1>>>
{
    // let rc4 = Rc4::new((&key).into());
    // rc4
    Arc4::with_key(key)
}

fn compare_bytes(s1: Vec<u8>, s2: Vec<u8>) -> bool
{
    s1 == s2
}

fn get_key() -> Vec<u8>
{
    vec![b'S' , b'i', b'm', b'p' ,b'l', b'e', b'K', b'e', b'y']
}

fn get_encoded_flag() -> Vec<u8>
{
    vec![0x4b, 0xec, 0x0e, 0x17, 0xe8, 0x92, 0x87, 0x65, 0xd4, 0xff, 0x15, 0xc7, 0x6b, 0xd9, 0x6a, 0x9d, 0x0f, 0xa3, 0xa0, 0x1c, 0x73, 0x24, 0x76, 0x2e, 0xff, 0x66, 0xc7, 0xa5, 0x84, 0x84, 0x86, 0xf3, 0x0a, 0x7e]
}

fn check_flag(s: String) -> bool
{
    let mut data = string_to_bytes(s);
    let key = get_key();
    let mut rc4 = new_rc4(&key);
    rc4.encrypt(&mut data);

    let expected = get_encoded_flag();

    compare_bytes(data, expected)
}

// fn check_flag2(s: String) -> String
// {
//     let mut data = string_to_bytes(s);
//     let key = get_key();
//     let mut rc4 = new_rc4(&key);
//     rc4.encrypt(&mut data);

//     let result = hex::encode(data);
//     result
// }


#[component]
pub fn FlagChecker(
    initial_value: String,
) -> impl IntoView {

    let (value, set_value) = create_signal(initial_value);
    let (response, set_response) = create_signal("".to_owned());
    view! {
        <div style="display: flex;flex-direction: column;align-items: center;">
            <input style="min-width:400px;" type="text" prop:value=value on:input=move |ev| {
                set_value(event_target_value(&ev));
            }/>
            <button on:click=move |_| {
                if check_flag(value())
                {
                    set_response("Ok".to_owned());
                }
                else
                {
                    set_response("Bad flag".to_owned());
                }
            }>"Check flag"</button>
            <br/>
            <span>{response}</span>

        </div>
    }
}
